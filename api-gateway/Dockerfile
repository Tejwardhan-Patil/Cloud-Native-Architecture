# Use official Golang base image for building the API Gateway
FROM golang:1.19 AS builder

# Set the working directory inside the container
WORKDIR /app

# Copy the Go modules manifest and download dependencies
COPY go.mod go.sum ./
RUN go mod download

# Copy the rest of the source code
COPY ./src ./src

# Build the API Gateway binary
RUN CGO_ENABLED=0 GOOS=linux go build -o /gateway ./src/gateway.go

# Start a new stage with a minimal base image
FROM alpine:3.18

# Install any necessary packages such as certificates
RUN apk add --no-cache ca-certificates

# Set working directory for the API Gateway in the minimal container
WORKDIR /root/

# Copy the built binary from the builder stage
COPY --from=builder /gateway .

# Copy configuration files
COPY ./config/gateway_config.yaml /etc/gateway/gateway_config.yaml

# Expose port for the API Gateway
EXPOSE 8080

# Define the entry point for the container
CMD ["./gateway", "-config", "/etc/gateway/gateway_config.yaml"]