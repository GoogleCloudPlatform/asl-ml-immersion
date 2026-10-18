# Advanced Solutions Lab

## 概要
このリポジトリには、Google Cloud 上で実行することを想定した AI および機械学習のコンテンツが含まれています。本リポジトリは Google Cloud の [Advanced Solutions Lab (ASL)](https://cloud.google.com/asl) チームによってメンテナンスされています。

本リポジトリには、さまざまな AI/ML トピックを網羅する主要な 3 つのモジュールが含まれています:
- `asl_core`: 主に TensorFlow と Keras で実装された、多様なデータモダリティ (テーブルデータ、画像、テキスト、時系列) を対象とする幅広いモデルアーキテクチャ (DNN、CNN、RNN、Transformer、SNGP など)。
- `asl_mlops`: TensorFlow、Scikit-learn、PyTorch モデルを大規模に本番運用化 (Agent Platform でのトレーニング、チューニング、サービング、および Kubeflow Pipelines 上での MLOps など) するための Google Cloud Agent Platform 上のツール群。
- `asl_genai`: Gemini や Google ADK などのエージェントフレームワークを使用した、生成 AI およびエージェントシステム。

## リポジトリの構成
各モジュール (`asl_core`、`asl_mlops`、`asl_genai`) には独立した環境と学習教材があり、各ディレクトリに整理されています。

すべての学習教材はコンテンツフォルダ内に配置されています。このフォルダはトピックごとに整理されており、各フォルダには `labs` と `solutions` フォルダが含まれています。TODO を埋めてコーディングスキルを実践するには `labs` のノートブックを使用し、コードの確認には `solutions` フォルダのノートブックを参照してください。

主な 3 つのフォルダ構成は以下のとおりです:

```
├── asl_core
│   ├── notebooks - トピックごとに整理された学習教材
│   │   ├── building_production_ml_systems
│   │   │   ├── labs
│   │   │   └── solutions
│   │   ├── end-to-end-structured
│   │   ├── image_models
│   │   ├── ...
│   ├── kernels - 特定のノートブックに必要なカーネルスクリプト
│   ├── scaffolds - AI/ML プロジェクトを加速するためのサンプルコード
│   ├── requirements.txt - このモジュールの依存関係
├── asl_mlops
│   ├── ...
├── asl_genai
│   ├── ...
├── ...
```

## 環境のセットアップ
### ステップ 1. Cloud Shell でセットアップスクリプトを実行する
本リポジトリは Agent Platform Workbench および Cloud Workstations でテストされています。まず、[Cloud Shell](https://shell.cloud.google.com) でセットアップスクリプトを実行し、必要なプロジェクトのインフラストラクチャ (API、IAM、バケット) を構成します。

[Cloud Shell](https://shell.cloud.google.com) でセットアップスクリプトを実行して環境をプロビジョニングします。
```bash
git clone --depth 1 -b asl_tok_202610 https://github.com/GoogleCloudPlatform/asl-ml-immersion.git
cd asl-ml-immersion
bash scripts/setup_env.sh
```

セットアップする環境の選択肢が表示されます:
*   **1) Agent Platform Workbench:** Agent Platform Workbench をセットアップします。
*   **2) Cloud Workstations:** Cloud Workstations をセットアップします。
*   **3) Setup both:** 両方の環境をセットアップします。
*   **4) Skip:** プロジェクトのインフラストラクチャ (API、IAM、バケット) のみをセットアップします。

オプション 1〜3 を選択して環境を自動的にセットアップするか、4 を選択して公式ドキュメントに従って手動で環境をセットアップします:
*   **Agent Platform Workbench:** [ユーザー管理のノートブック インスタンスを作成する](https://docs.cloud.google.com/gemini-enterprise-agent-platform/notebooks/workbench/instances/create-console-quickstart)
*   **Cloud Workstations:** [ワークステーションを作成する](https://docs.cloud.google.com/workstations/docs/create-workstation)

次に、環境に GPU (Nvidia T4) を接続するかどうかを確認されます。希望に応じて `y` または `n` を選択してください。

**注:** ほとんどのノートブックではアクセラレータ (GPU/TPU) は必須ではありませんが、一部のノートブックでは使用が推奨されています。

### ステップ 2. 環境の構築
環境が起動したら、それを開きます。次に、**環境内のターミナル**で以下のコマンドを実行してこのリポジトリをクローンし、環境 (仮想環境 (venv) および Jupyter カーネル) を構築します。

```bash
git clone --depth 1 -b asl_tok_202610 https://github.com/GoogleCloudPlatform/asl-ml-immersion.git
cd asl-ml-immersion
make
```

Cloud Workstations では、`Open Folder` -> `asl-ml-immersion` をクリックしてリポジトリのウィンドウを開きます。すでにフォルダが開いている場合は、`Command + Shift + P` を押して `Developer: Reload Window` と入力し、変更を反映させます。

## 環境の使い方
### ノートブックの実行
上記のセットアップ完了後、Jupyter ノートブックファイルを開き、各モジュールのカーネル (`ASL Core`、`ASL MLOps`、または `ASL Agent`) で実行できます。<br>
適切なカーネルがあらかじめ選択されていない場合は、`Select Kernel` をクリックして適切なものを選択してください。

**Cloud Workstations の場合**: `Select Kernel` -> `Jupyter Kernels` の下にカーネルが表示されます。<br>
`Jupyter Kernels` が見つからない場合は、`Python Environment` -> `<- (左矢印)` をクリックして環境を再読み込みしてください。

**注**: 一部のノートブックでは追加のセットアップが必要な場合があります。各ノートブック内の指示を参照してください。

### ターミナルでのコマンド実行
ターミナルからコマンドを実行する際は、対象の環境に対応する venv をアクティベートしてください。

例 (asl-ml-immersion ディレクトリ配下):
```bash
source ./asl_genai/.venv/bin/activate
adk web ./asl_genai/notebooks/building_agents/solutions/adk_agents
```

## 貢献 (Contributions)
現在、このリポジトリに貢献できるのは Googler のみです。コントリビューションのワークフローの詳細については、[CONTRIBUTING.md](https://github.com/GoogleCloudPlatform/asl-ml-immersion/blob/master/CONTRIBUTING.md) を参照してください。

## 免責事項 (Disclaimer)
これは公式にサポートされている Google の製品ではありません。Google Cloud 製品の使用には料金が発生します。料金についての詳細は[こちら](https://cloud.google.com/pricing)をご確認ください。

## ライセンス (Licensing)
このリポジトリのすべてのコードは Apache License, Version 2.0 (以下「ライセンス」) の下でライセンス供与されています。ライセンスのコピーは[こちら](https://www.apache.org/licenses/LICENSE-2.0)から取得できます。

*Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License*
