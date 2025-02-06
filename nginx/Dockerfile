# Use the official Nginx image as the base image
FROM nginx:alpine

# Copy custom Nginx config
COPY nginx.conf /etc/nginx/nginx.conf

# Expose ports
EXPOSE 80

# Make sure Nginx is running
CMD ["nginx", "-g", "daemon off;"]