FROM ghcr.io/gleam-lang/gleam:v1.5.1-erlang-alpine AS build
WORKDIR /app
COPY . .
RUN gleam export erlang-shipment

FROM erlang:27-alpine
RUN apk add --no-cache sqlite-libs
WORKDIR /app
COPY --from=build /app/build/erlang-shipment ./
EXPOSE 8000
ENV PORT=8000
ENTRYPOINT ["./entrypoint.sh", "run"]
