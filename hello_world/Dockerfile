FROM amazon/aws-lambda-python:3.9

RUN apt-get install -y libmysqlclient-dev
RUN pip install mysql

CMD ["app.lambda_handler"]