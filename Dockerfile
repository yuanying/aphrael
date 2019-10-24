FROM ruby:2.5.5-alpine as builder

RUN apk --update add --virtual build-dependencies \
    build-base \
    curl-dev \
    linux-headers
ENV BUNDLER_VERSION 2.0.1
RUN gem install bundler
WORKDIR /tmp
COPY Gemfile Gemfile
COPY Gemfile.lock Gemfile.lock
ENV BUNDLE_JOBS=4
RUN bundle install
RUN apk del build-dependencies

FROM ruby:2.5.5-alpine
# RUN echo "@main http://dl-cdn.alpinelinux.org/alpine/edge/main" >> /etc/apk/repositories
# RUN apk --update add libstdc++@main gcc@main
RUN apk --update add \
    bash \
    libc-dev \
    libstdc++ \
    gcc \
    imagemagick
RUN ln -s /usr/lib/libstdc++.so.6 /usr/lib/libstdc++.so
ENV BUNDLER_VERSION 2.0.1
RUN gem install bundler

WORKDIR /tmp
COPY Gemfile Gemfile
COPY Gemfile.lock Gemfile.lock
COPY --from=builder /usr/local/bundle /usr/local/bundle

ENV APP_HOME /myapp
RUN mkdir -p $APP_HOME
WORKDIR $APP_HOME
COPY . $APP_HOME

EXPOSE 9292
CMD ["bundle", "exec", "rackup", "-o", "0.0.0.0"]