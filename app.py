import boto3
import botocore.config
import json
from datetime import datetime


def bedrock_blog_generator(blog_topic: str) -> str:
    """
    Generate a blog post using Amazon Bedrock's LLM.

    Args:
        blog_topic (str): The topic for the blog post.

    Returns:
        str: The generated blog post.
    """
    # Initialize the Bedrock client
    try:
        bedrock = boto3.client(
            'bedrock-runtime',
            region_name='us-east-1',
            config=botocore.config.Config(
                read_timeout=300,
                retries={
                    'max_attempts': 3,
                    'mode': 'standard'
                }
            )
        )

        # Define the model and prompt
        model_id = "meta.llama3-70b-instruct-v1:0"
        payload = {
            "prompt": f"<|begin_of_text|>Assistant: Write a 200 words blog post about {blog_topic} <|end_of_text|>",
            "max_gen_len": 512,
            "temperature": 0.7,
            "top_p": 0.9
        }

        # Invoke LLaMA 3 model
        response = bedrock.invoke_model(
            modelId=model_id,
            body=json.dumps(payload),
            contentType='application/json'
        )

        response_content = response.get('body').read()
        response_data = json.loads(response_content)
        print(response_data)
        blog_details = response_data.get('generation', 'Warning: No content generated')

        return blog_details
    except Exception as e:
        print(f"An error occurred: {e}")
        return "Error generating blog post."


def save_blog_to_s3(blog_content: str, s3_key: str):
    """
    Save the generated blog content to an S3 bucket.

    Args:
        blog_content (str): The content of the blog post.
        s3_key (str): The S3 key where the blog post will be saved.
    """
    s3 = boto3.client('s3')
    s3_bucket = "aws-bedrock-blog-posts-hexa"

    try:
        s3.put_object(
            Bucket=s3_bucket,
            Key=s3_key,
            Body=blog_content
        )
        print(f"Blog post saved to S3 bucket {s3_bucket} with key {s3_key}")
    except Exception as e:
        print(f"An error occurred while saving to S3: {e}")


def lambda_handler(event, context):
    # TODO implement
    event = json.loads(event['body'])
    blog_topic = event.get('blog_topic')

    generate_blog = bedrock_blog_generator(blog_topic=blog_topic)

    if generate_blog:
        current_time = datetime.now().strftime("%Y%m%d_%H:%M:%S")
        s3_key = f"blog_posts/{current_time}.txt"
        save_blog_to_s3(generate_blog, s3_key)

        return {
            'statusCode': 200,
            'body': json.dumps("Blog post generated and saved successfully"),
        }
    else:
        return {
            'statusCode': 500,
            'body': json.dumps('Error generating blog post')
        }

# https://bfci8xcd58.execute-api.us-east-1.amazonaws.com/dev
# /blog-generation
# s3, admin