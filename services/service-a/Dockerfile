# Base image for Go language
FROM golang:1.18-alpine AS builder

# Set the working directory inside the container
WORKDIR /app

# Copy Go modules and Go source files
COPY src/go.mod src/go.sum ./
RUN go mod download

# Copy the source code to the working directory
COPY src/ .

# Build the Go application
RUN go build -o service-a main.go

# Final stage: create a minimal container for the Go application
FROM alpine:latest
WORKDIR /root/

# Copy the compiled Go binary from the builder stage
COPY --from=builder /app/service-a .

# Expose the service port
EXPOSE 8080

# Run the Go service
CMD ["./service-a"]