FROM ruby:2.4.4-alpine as builder

RUN echo "@testing http://dl-cdn.alpinelinux.org/alpine/edge/testing" >> /etc/apk/repositories
RUN apk --update add freeimage-dev@testing
RUN apk --update add --virtual build-dependencies \
    build-base \
    curl-dev \
    linux-headers
RUN gem install bundler
WORKDIR /tmp
COPY Gemfile Gemfile
COPY Gemfile.lock Gemfile.lock
ENV BUNDLE_JOBS=4
RUN bundle install
RUN apk del build-dependencies

FROM ruby:2.4.4-alpine
RUN echo "@testing http://dl-cdn.alpinelinux.org/alpine/edge/testing" >> /etc/apk/repositories
# RUN echo "@main http://dl-cdn.alpinelinux.org/alpine/edge/main" >> /etc/apk/repositories
RUN apk --update add freeimage-dev@testing
# RUN apk --update add libstdc++@main gcc@main
RUN apk --update add \
    bash \
    libc-dev \
    libstdc++ \
    gcc
RUN ln -s /usr/lib/libstdc++.so.6 /usr/lib/libstdc++.so
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