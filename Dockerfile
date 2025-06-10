FROM node:20-slim

RUN npm install -g topojson-server topojson-simplify topojson-client

WORKDIR /data
