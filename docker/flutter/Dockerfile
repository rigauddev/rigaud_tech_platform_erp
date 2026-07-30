FROM ghcr.io/cirruslabs/flutter:3.41.9

USER root
RUN chown -R ubuntu:ubuntu /sdks/flutter /home/ubuntu \
    && su ubuntu -c "git config --global --add safe.directory /sdks/flutter"

WORKDIR /workspace

EXPOSE 3000

CMD ["sh", "-lc", "chown -R ubuntu:ubuntu /home/ubuntu/.pub-cache && su ubuntu -c 'cd /workspace && /sdks/flutter/bin/flutter pub get && /sdks/flutter/bin/flutter run -d web-server --web-hostname 0.0.0.0 --web-port 3000'"]
