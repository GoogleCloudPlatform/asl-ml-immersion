package com.google.cloud.training.aslmlimmersion;

import java.io.IOException;
import java.security.GeneralSecurityException;
import java.util.ArrayList;
import java.util.List;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.google.api.client.googleapis.auth.oauth2.GoogleCredential;
import com.google.api.client.googleapis.javanet.GoogleNetHttpTransport;
import com.google.api.client.http.ByteArrayContent;
import com.google.api.client.http.GenericUrl;
import com.google.api.client.http.HttpBackOffUnsuccessfulResponseHandler;
import com.google.api.client.http.HttpContent;
import com.google.api.client.http.HttpRequest;
import com.google.api.client.http.HttpRequestFactory;
import com.google.api.client.http.HttpTransport;
import com.google.api.client.util.ExponentialBackOff;
import com.google.cloud.training.aslmlimmersion.Baby.INPUTCOLS;
import com.google.gson.Gson;
import com.google.gson.GsonBuilder;

public class BabyweightMLService {
  private static final Logger LOG = LoggerFactory.getLogger(BabyweightMLService.class);
  private static final String PROJECT = "asl-ml-immersion";  // TODO: put in your project name here
  private static String       MODEL   = "babyweight";
  private static String       VERSION = "v1";

  static class Request {
    // TODO: map this Java class to your JSON input structure
  }

  static class Prediction {
    // TODO: map this Java class to your JSON output structure
  }

  static class Response {
    List<Prediction> predictions = new ArrayList<>();

    public double[] getPredictedBabyWeights() {
      double[] result = new double[predictions.size()];
      // TODO: set the result values
      return result;
    }
  }

  static Response sendRequest(Request req) throws IOException, GeneralSecurityException {
    long startTime = System.currentTimeMillis();
    try {
      // create JSON of request
      Gson gson = new GsonBuilder().create();
      String json = null; // TODO: create JSON of request

      // our service's URL
      String endpoint = "https://ml.googleapis.com/v1/projects/" 
          + String.format("%s/models/%s/versions/%s:predict", PROJECT, MODEL, VERSION);
      GenericUrl url = new GenericUrl(endpoint);

      // set up https
      GoogleCredential credential = GoogleCredential.getApplicationDefault();
      HttpTransport httpTransport = GoogleNetHttpTransport.newTrustedTransport();
      HttpRequestFactory requestFactory = httpTransport.createRequestFactory(credential);
      HttpContent content = new ByteArrayContent("application/json", json.getBytes());
      
      // send request     
      String response = null; // TODO: send request and get back response as string
      
      // parse response
      return gson.fromJson(response, Response.class);
    }
    finally {
      long endTime = System.currentTimeMillis();
      LOG.debug((endTime - startTime) + " msecs overall");
    }
  }
  
  public static double[] mock_batchPredict(Iterable<Baby> instances) throws IOException, GeneralSecurityException {
    int n = 0;
    for (@SuppressWarnings("unused") Baby f : instances) {
      ++n;
    }
    LOG.info("Mock prediction for " + n + " instances");
    double[] result = new double[n];
    for (int i=0; i < n; ++i) {
      result[i] = Math.random() * 10;
    }
    return result;
  }
  
  public static double[] batchPredict(Iterable<Baby> instances) throws IOException, GeneralSecurityException {
    Request request = null; // TODO: create request containing information from instances
    Response resp = sendRequest(request);
    double[] result = resp.getPredictedBabyWeights();
    return result;
  }

  public static double predict(Baby f, double defaultValue) throws IOException, GeneralSecurityException {
    
      Request request = null;  // TODO: create request containing information from Baby f

      // send request
      Response resp = sendRequest(request);
      double[] result = resp.getPredictedBabyWeights();
      if (result.length > 0) {
        return result[0];
      } else {
        return defaultValue;
      }
    
  }

  public static void main(String[] args) throws Exception {
    Baby f = Baby.fromCsv("7.27084540076,True,28,White,1,40.0,True,,,somekey");
    System.out.println("predicted=" + predict(f, -1) + " actual=" + f.getFieldAsFloat(INPUTCOLS.weight_pounds));
  }

}
