# WorkReminder

<div lang="en">

## English

- Create a WorkReminder bot using AWS Lambda, Telegram, and the OpenAI API.
- The system is constructed utilizing the `API proxy` pattern.

### Prerequisites
- An AWS account.
- A Telegram bot token (you can get one by creating a bot with BotFather on Telegram).
- OpenAI API key for accessing ChatGPT.
- Basic knowledge of Python and AWS Lambda.

### Architecture


![TaskReminder](https://github.com/mingyu110/Cloud-and-GenAI/assets/48540798/6b68f291-a342-419e-9504-91492f5738a2)

### Step1: Setting Up the Telegram Bot
1. Create a Telegram Bot:
   - Open Telegram and search for @BotFather.
   - Start a conversation and use the /newbot command to create a new bot.
   - Follow the prompts to name your bot and get the token. Save this token for later use.

### Step2: Setting Up AWS Services
All the mentioned codes can be found here: [WorkReminder](https://github.com/mingyu110/Cloud-and-GenAI/WorkReminder-with-OpenAI-and-Lambda)

### Step3: Creating a RDS MySQL Database
1. Create a RDS MySQL Instance
2. Create the DataBase Schema
```sql
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    chat_id VARCHAR(15) UNIQUE,
    user_score INT DEFAULT 0
);

CREATE TABLE taskreminder  (
    id INT AUTO_INCREMENT PRIMARY KEY,
    chat_id VARCHAR(15),
    task_name VARCHAR(255),
    time TIME,
    notification_status ENUM('pending', 'confirmed', 'missed') DEFAULT 'pending',
    notification_timestamp DATETIME
);
```
### Step4: Configure OpenAI API
Configure an OpenAI API that will answer your patient questions based on their medications and the model you choose. Save your OpenAI Key.

### Step5: Create S3 Bucket
Create an S3 bucket that stores the quotes images to send to your users and store your S3 Bucket Name.

### Step6: Creating Lambda Functions
- **Dispatcher Lambda Function**: This function acts as the central router for incoming Telegram messages. It parses the message, identifies the command, and invokes the appropriate Lambda function (e.g., Add, Summary, ChatGPT).
- **ChatGPT Lambda Function**: This function handles user queries that start with <mark>/question</mark>. It fetches the user's medication data, constructs a prompt, and sends it to the ChatGPT API. The response from ChatGPT is then sent back to the user.
- **Add Lambda Function**: This function processes requests to add new work tasks. It extracts the work task details from the message, validates them, and stores them in the RDS MySQL database.
- **Summary Lambda Function**: This function retrieves and sends a summary of the user's work tasks. When a user sends a <mark>/summary</mark> command, this function queries the database for all work tasks associated with the user and sends a formatted list back to the user.
- **Notification Lambda Function**: This function is triggered by a scheduled EventBridge cron job to send work task reminders to users. It queries the database for taskreminders that need to be taken in the next hour and sends reminder messages via Telegram.
- **User Response Lambda Function**: This function handles responses from users confirming whether they have taken their work task. It updates the task status in the database and adjusts the user's score based on their response.
- **Missed Task Lambda Function**: This function is triggered by a scheduled EventBridge cron job to check for missed tasks. It identifies tasks that were not confirmed as taken and updates their status to missed in the database. It also adjusts the user's score accordingly.
- **Motivational Lambda Function**: This function sends motivational messages or images to users at scheduled times or when they miss taking their task. It selects a random motivational image from an S3 bucket and sends it to the user via Telegram.

The environment variables should be properly populated in each Lambda function, and the dependencies listed in requirements.txt should be linked as a Layer.

### Step7: Configure the EventBridge Schedules
Set up two cron jobs using EventBridge. The first job, scheduled to run at <mark>00 * * * ? *</mark>, will trigger the Notification Lambda Function. The second job, set for <mark>15 * * * ? *</mark>, will invoke the Missed Task Lambda Function. Additionally, create a third cron job to send motivational pictures randomly or when tasks are missed according to your preferences.

### Step8: Setting Up API Gateway
- Create an API Gateway:
  - Go to the API Gateway console and create a new REST API.
  - Create a new resource and set up a POST method.
  - Configure the POST method to trigger the Dispatcher Lambda function.
- Set Up Telegram Webhook:
  - Set the webhook URL to point to the API Gateway endpoint:
   ```sql
    https://api.telegram.org/bot<YOUR_TELEGRAM_BOT_TOKEN>/setWebhook?url=https://<YOUR_API_GATEWAY_URL>/webhook
   ```

</div>

<div lang="zh">

## 中文

- 使用AWS Lambda、OpenAI API创建的用于Telegram的工作任务提醒机器人。
- 该系统基于`API Proxy`模式进行构建。

### 前置条件
- AWS账户
- Telegram bot token(可以在Telegram上使用@BotFather创建
- 用于访问ChatGPT的OpenAI API密钥
- 具备Python和AWS Lambda的基础知识

### 架构


![TaskReminder](https://github.com/mingyu110/Cloud-and-GenAI/assets/48540798/b01ce495-8d2e-48d7-ab29-9122121bd572)

### 步骤1: 设置Telegram Bot
1. 创建Telegram Bot:
   - 在Telegram中搜索@BotFather并打开对话框
   - 使用命令`/newbot`创建一个全新的机器人
   - 按照提示为其命名和获取令牌，请务必妥善保存该令牌以备将来使用
### 步骤2: 设置AWS服务
所有所提及的代码均可在此处获取：[WorkReminder](https://github.com/mingyu110/Cloud-and-GenAI/WorkReminder-with-OpenAI-and-Lambda)

</div>
