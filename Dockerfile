FROM ruby:2.4.4-slim
MAINTAINER O. Yuanying "yuan-docker@fraction.jp"

RUN apt-get update && apt-get install -y libfreeimage-dev
EXPOSE 9292
CMD ["bundle", "exec", "rackup", "-o", "0.0.0.0"]
