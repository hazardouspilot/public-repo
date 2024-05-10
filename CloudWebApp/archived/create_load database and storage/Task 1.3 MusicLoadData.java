// Copyright 2012-2015 Amazon.com, Inc. or its affiliates. All Rights Reserved.

package com.amazonaws.samples;

import com.amazonaws.auth.profile.ProfileCredentialsProvider;
import com.amazonaws.regions.Regions;
import com.amazonaws.services.dynamodbv2.AmazonDynamoDB;
import com.amazonaws.services.dynamodbv2.AmazonDynamoDBClientBuilder;
import com.amazonaws.services.dynamodbv2.document.DynamoDB;
import com.amazonaws.services.dynamodbv2.document.Item;
import com.amazonaws.services.dynamodbv2.document.Table;
import com.fasterxml.jackson.core.JsonFactory;
import com.fasterxml.jackson.core.JsonParser;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;

import java.io.File;

public class MusicLoadData {

    public static void main(String[] args) throws Exception {

        AmazonDynamoDB client = AmazonDynamoDBClientBuilder.standard()
                .withRegion(Regions.US_EAST_1)
                .withCredentials(new ProfileCredentialsProvider("default"))
                .build();

        DynamoDB dynamoDB = new DynamoDB(client);

        Table table = dynamoDB.getTable("music");

        JsonParser parser = new JsonFactory().createParser(new File("a1.json"));

        JsonNode rootNode = new ObjectMapper().readTree(parser);
        JsonNode songsNode = rootNode.get("songs");

        for (JsonNode songNode : songsNode) {
            int year = songNode.path("year").asInt();
            String title = songNode.path("title").asText();
            String artist = songNode.path("artist").asText();
            String webUrl = songNode.path("web_url").asText();
            String imgUrl = songNode.path("img_url").asText();

            try {
                table.putItem(new Item()
                        .withPrimaryKey("year", year, "title", title)
                        .withString("artist", artist)
                        .withString("web_url", webUrl)
                        .withString("img_url", imgUrl));
                System.out.println("PutItem succeeded: " + year + " " + title);
            } catch (Exception e) {
                System.err.println("Unable to add song: " + year + " " + title);
                System.err.println(e.getMessage());
            }
        }
        parser.close();
    }
}