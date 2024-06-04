FROM public.ecr.aws/lambda/python:3.12

# Install Python dependencies
COPY requirements.txt /var/task/
RUN pip install -r /var/task/requirements.txt --target /var/task

# Copy the Lambda function code
COPY app.py /var/task/

# Set the working directory
WORKDIR /var/task

# Set the CMD to your handler
CMD ["app.lambda_handler"]