# Deploying AgroSmart to AWS EC2

This runs the whole stack (FastAPI + Streamlit) on one Ubuntu EC2 instance using Docker Compose.
Only the Streamlit port (8501) needs to be public; the frontend reaches the API over Docker's internal network.

## 1. Launch the instance (AWS Console -> EC2 -> Launch instance)
- **AMI:** Ubuntu Server 24.04 LTS
- **Instance type:** `t3.small` (2 GB RAM). A 1 GB instance can run out of memory while the image trains the model during the build. Check your account's free-tier or credit status before choosing.
- **Key pair:** create one and download the `.pem` file.
- **Security group (inbound rules):**
  - SSH, port 22, source **My IP**
  - Custom TCP, port 8501, source `0.0.0.0/0` (the Streamlit app)
  - Do **not** open port 8000 publicly unless you want the raw API exposed.
- **Storage:** 16 GB gp3 is enough.

## 2. Connect
```bash
chmod 400 ~/Downloads/your-key.pem
ssh -i ~/Downloads/your-key.pem ubuntu@<EC2_PUBLIC_IP>
```

## 3. Install Docker
```bash
sudo apt-get update
sudo apt-get install -y docker.io docker-compose-v2 git
sudo systemctl enable --now docker
sudo usermod -aG docker ubuntu
exit      # log out, then SSH back in so the group change applies
```

## 4. Get the code and add your key
```bash
git clone https://github.com/asminaithani/agrosmart.git
cd agrosmart
nano .env
```
Put this single line in `.env`, then save (Ctrl+O, Enter, Ctrl+X). Never commit this file.
```
GROQ_API_KEY=your_real_key_here
```

## 5. Build and start
```bash
docker compose up -d --build
docker compose ps
```
The first build takes a few minutes (it trains the model). Both services should show `running`, and the API as `healthy`.

## 6. Open the app
Visit `http://<EC2_PUBLIC_IP>:8501` in your browser.

Quick checks from the instance:
```bash
curl -s http://localhost:8000/health
docker compose logs --tail=50 api
```

## 7. Updating after a code change
```bash
cd agrosmart
git pull
docker compose up -d --build
```

## 8. Stop paying when you are done
- Stop the stack: `docker compose down`
- In the EC2 console, **Stop** the instance (keeps the disk) or **Terminate** it (deletes everything).
- If you attached an Elastic IP, release it, since unattached Elastic IPs are billed.

## Notes
- The public IP changes every time you stop and start the instance, unless you attach an Elastic IP.
- This setup serves plain HTTP. For anything beyond a demo, put it behind a reverse proxy with HTTPS.
- Prediction history lives in the `agro-data` Docker volume, so it survives `docker compose restart` but not instance termination.
