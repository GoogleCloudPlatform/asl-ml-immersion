"""Classes and factories for quering GCP services."""

import os

from app import lib
from app.settings import Config
from google.cloud import aiplatform
from langchain.chains import RetrievalQA
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_community.document_loaders import DataFrameLoader
from langchain_google_vertexai import VertexAI, VertexAIEmbeddings


class StorageService:
    """Light front to GCS."""

    def __init__(self, bucket_name, local_dir):
        self.bucket_name = bucket_name.replace("gs://", "")
        self.local_dir = os.path.abspath(local_dir)
        if not os.path.exists(self.local_dir):
            os.makedirs(self.local_dir)

    def upload(self, relative_path_in_local_dir, bucket_prefix=None):
        folder_path = os.path.join(self.local_dir, relative_path_in_local_dir)
        lib.upload_directory_to_gcs(
            bucket_name=self.bucket_name,
            folder_path=folder_path,
            bucket_prefix=bucket_prefix,
        )

    def download(self, bucket_prefix):
        lib.download_directory_from_gcs(
            bucket_name=self.bucket_name,
            local_folder=self.local_dir,
            bucket_prefix=bucket_prefix,
        )


def create_storage_service():
    return StorageService(
        bucket_name=Config.BUCKET,
        local_dir=Config.LOCAL_STORAGE,
    )


class CSVDocumentStore:
    """Generic Store for single CSV files"""

    def __init__(
        self,
        raw_data_path,
        content_columns,
        metadata_columns,
    ):
        self._data_path = raw_data_path
        self._content_columns = content_columns
        self._metadata_columns = metadata_columns
        self._raw_data = None
        self._processed_data = None

    @property
    def raw_data(self):
        if self._raw_data is None:
            self._raw_data = lib.load_csv_as_df(self._data_path)
        return self._raw_data

    @property
    def processed_data(self):
        if self._processed_data is None:
            self._processed_data = self._process_raw_data()
        return self._processed_data

    def _process_raw_data(self):
        return lib.create_content_df(
            df=self.raw_data,
            content_columns=self._content_columns,
            metadata_columns=self._metadata_columns,
        )


def create_datasheet_service():
    return CSVDocumentStore(
        raw_data_path=Config.DATASHEET_PATH,
        content_columns=Config.DATASHEET_CONTENT_COLUMNS,
        metadata_columns=Config.DATASHEET_METADATA_COLUMNS,
    )


class RAGService:
    """Retrieval Augmented Generation Service."""

    STORAGE_NAME = "vectorstore"
    CONTENT_COLUMNS = "content"

    def __init__(
        self,
        embedding_engine,
        llm_engine,
        document_svc,
        storage_svc,
        chunk_size,
        chunk_overlap,
        search_type,
        nearest_neighbors,
    ):
        self.embedding_engine = embedding_engine
        self.llm_engine = llm_engine
        self.storage_svc = storage_svc
        self.document_svc = document_svc
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.search_type = search_type
        self.nearest_neighbors = nearest_neighbors
        self.local_vector_path = os.path.join(
            self.storage_svc.local_dir, self.STORAGE_NAME
        )
        self._vector_store = None
        self._retriever = None
        self._chain = None

    @property
    def vector_store(self):
        if self._vector_store is None:
            self.storage_svc.download(self.STORAGE_NAME)
            self._vector_store = Chroma(
                persist_directory=self.local_vector_path,
                embedding_function=self.embedding_engine,
            )
        return self._vector_store

    @property
    def retriever(self):
        if self._retriever is None:
            self._retriever = self.vector_store.as_retriever(
                search_type=self.search_type,
                search_kwargs={"k": self.nearest_neighbors},
            )
        return self._retriever

    @property
    def chain(self):
        if self._chain is None:
            self._chain = RetrievalQA.from_chain_type(
                llm=self.llm_engine,
                chain_type="stuff",
                retriever=self.retriever,
                return_source_documents=True,
            )
        return self._chain

    def generate_embeddings(self):
        docs_df = self.document_svc.processed_data
        loader = DataFrameLoader(
            docs_df, page_content_column=self.CONTENT_COLUMNS
        )
        print("generate_embeddings: loading docs")
        docs = loader.load()
        print("generate_embeddings: splitting docs")
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
        )
        chunks = text_splitter.split_documents(docs)
        print("generate_embeddings: creating the vector store")
        Chroma.from_documents(
            chunks,
            self.embedding_engine,
            persist_directory=self.local_vector_path,
        )
        print("generate_embeddings: uploading the vector store")
        self.storage_svc.upload(self.STORAGE_NAME)

    def query(self, prompt):
        return self.chain.invoke({"query": prompt})


def create_rag_service():
    aiplatform.init(
        project=Config.PROJECT,
        location=Config.LOCATION,
        staging_bucket=Config.BUCKET,
    )
    embedding = VertexAIEmbeddings(
        model_name=Config.GEMINI_EMBBEDING_MODEL,
    )
    llm = VertexAI(
        model_name=Config.GEMINI_TEXT_MODEL,
        temperature=Config.GEMINI_TEMPERATURE,
        max_output_tokens=Config.GEMINI_MAX_OUTPUT_TOKENS,
        top_p=Config.GEMINI_TOP_P,
        top_k=Config.GEMINI_TOP_K,
    )
    return RAGService(
        embedding_engine=embedding,
        llm_engine=llm,
        document_svc=create_datasheet_service(),
        storage_svc=create_storage_service(),
        chunk_size=Config.RETRIEVAL_CHUNK_SIZE,
        chunk_overlap=Config.RETRIEVAL_OVERLAP_SIZE,
        search_type=Config.RETRIEVAL_SEARCH_TYPE,
        nearest_neighbors=Config.RETRIEVAL_NEAREST_NEIGHBORS,
    )
