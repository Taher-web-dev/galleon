FROM alpine:3.16

# Optional external mount points
VOLUME ["/home"]

# Copy sample project python source code
ADD backend /home/backend/

# Install required run-time packages
RUN apk add --no-cach python3 py3-requests py3-jwt py3-six py3-sqlalchemy libpq py3-jinja2 py3-pydantic py3-bcrypt py3-psycopg2 py3-wheel py3-passlib py3-gunicorn

# Install required pips (from backend/requirments.txt) along with disposable build tools
RUN apk add --no-cache --virtual devstuff py3-pip  \
  && pip3 install -r /home/backend/requirements.txt \
  && pip3 cache purge \
  && apk del --no-cache devstuff

CMD ["ash"]
