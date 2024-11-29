FROM nginx:1.27.2-alpine
RUN mkdir -p /app/static /app/media

RUN rm /etc/nginx/nginx.conf /etc/nginx/conf.d/default.conf

RUN chown -R nginx:nginx /app && \
    chmod -R 755 /app

RUN apk add --no-cache gettext

COPY nginx.conf /etc/nginx/nginx.conf.template
COPY nginx-entrypoint.sh /nginx-entrypoint.sh
RUN chmod +x /nginx-entrypoint.sh

ENTRYPOINT ["/nginx-entrypoint.sh"]
CMD ["nginx", "-g", "daemon off;"]