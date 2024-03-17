# Use an official Node.js runtime as a base image
FROM node:latest

# Install Git
RUN apt-get update && \
    apt-get install -y git

# Set the working directory in the container
WORKDIR /app

# Copy package.json and package-lock.json to the working directory
COPY package*.json ./

# Install Node.js dependencies
RUN npm install

# Copy the rest of your application code
COPY index.js ./

# Define the command to run your application
CMD ["node", "index.js"]
