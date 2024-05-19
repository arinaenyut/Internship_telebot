FROM python:3-alpine

WORKDIR /bot

COPY . .

RUN apk add --no-cache gcc musl-dev postgresql-dev

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python3", "bot.py"]
