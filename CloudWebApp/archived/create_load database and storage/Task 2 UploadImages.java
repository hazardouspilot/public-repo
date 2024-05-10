// Adapted from code provided in RMIT practical class

package com.amazonaws.samples;

import com.amazonaws.AmazonServiceException;
import com.amazonaws.SdkClientException;
import com.amazonaws.regions.Regions;
import com.amazonaws.services.s3.AmazonS3;
import com.amazonaws.services.s3.AmazonS3ClientBuilder;
import com.amazonaws.services.s3.model.ObjectMetadata;
import com.amazonaws.services.s3.model.PutObjectRequest;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;

import java.io.File;
import java.io.IOException;
import java.io.InputStream;
import java.net.URL;

public class UploadImages {

    public static void main(String[] args) throws IOException {
        Regions clientRegion = Regions.US_EAST_1;
        String bucketName = "s3997902-bucket-public";
        String jsonFileName = "a1.json";

        try {
            AmazonS3 s3Client = AmazonS3ClientBuilder.standard()
                    .withRegion(clientRegion)
                    .build();

            ObjectMapper objectMapper = new ObjectMapper();
            JsonNode rootNode = objectMapper.readTree(new File(jsonFileName));
            JsonNode songsNode = rootNode.get("songs");

            for (JsonNode songNode : songsNode) {
                String title = songNode.path("title").asText();
                int year = songNode.path("year").asInt();
                String imgUrl = songNode.path("img_url").asText();

                try (InputStream inputStream = new URL(imgUrl).openStream()) {
                    ObjectMetadata metadata = new ObjectMetadata();
                    metadata.setContentType("image/jpeg"); // Assuming JPEG images, change accordingly
                    metadata.addUserMetadata("title", title);
                    metadata.addUserMetadata("year", String.valueOf(year));
                    PutObjectRequest request = new PutObjectRequest(bucketName, title + "_" + year + ".jpg", inputStream, metadata);
                    s3Client.putObject(request);
                    System.out.println("Uploaded image: " + title + "_" + year + ".jpg");
                } catch (IOException e) {
                    e.printStackTrace();
                }
            }

        } catch (AmazonServiceException e) {
            // The call was transmitted successfully, but Amazon S3 couldn't process 
            // it, so it returned an error response.
            e.printStackTrace();
        } catch (SdkClientException e) {
            // Amazon S3 couldn't be contacted for a response, or the client
            // couldn't parse the response from Amazon S3.
            e.printStackTrace();
        }
    }
}

