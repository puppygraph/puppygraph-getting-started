FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Accept build argument
ARG PUPPYGRAPH_HOST=localhost
ENV PUPPYGRAPH_HOST=$PUPPYGRAPH_HOST

# Build the application
RUN npm run build

# Expose port
EXPOSE 3000

# Start the application
CMD ["npm", "start"]