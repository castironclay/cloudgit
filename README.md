# Cloud GIT
Combining Cloudflared tunnels, websockets, and Github workflows for testing purposes. No service purchasing necessary. 

This is all for research purposes as I learn more about ways I could route packets across the internet while getting better at Python. Many items within this project could likely be improved and you should use at your own risk. 

### Requirements 
Ensure these applications are available your machine. `/usr/local/bin/cloudflared` is the expected path for the cloudflared binary. All others will be executed outside of the automated workflow and can be located anywhere on your machine. 

- [wiregaurd](https://www.wireguard.com/install/])<br />
Why? I wanted to build a tunnel from my local machine, or any machine with wireguard, to my workflow runner to permit full layer 3 routing out to the internet and not just a socks proxy. 

- [wstunnel](https://github.com/erebe/wstunnel/releases)<br />
Why? We are using a cloudflared tunnel running on our free Github runner. We can use wstunnel to create a websocket along with a local port forward to send our Wireguard UDP traffic from our local machine to our Github runner. wstunel is a powerful tool and its worth exploring all of its options. 

- [cloudflared](https://github.com/cloudflare/cloudflared/releases)<br />
Why? Cause it's awesome, and it can give us remote connectivity to devices behind NAT. In this project we are using the free [trycloudflare](https://try.cloudflare.com/) tunnels where we get random domains for free but with no guaranteed SLA or up-time. That tunnel on our Github workflow runner is used to build the our websocket and ultimately our wireguard connection by tunneling UDP across. 

## Github credentials file
This is the format of your `keys.yaml` file containing the required Github account details for where your workflows will be running.

```yaml
# keys.yaml
---
github1:
  key: API_KEY
  account: GITHUB_ACCOUNT_NAME
  repo: GITHUB_REPO_NAME
  file: githubmesh.yml
```

## Order of events
1. Local Cloudflared listener is created and URL is captured.
2. Github workflow is initiated and verified to be running with our local Cloudflared URL being passed as a workflow input.
3. Local httpd server started to receive the incoming GET requests from our Github workflow. Workflow -> Cloudflare -> Cloudflared tunnel -> httpd listener
4. Wireguard config is received and decoded.
5. URL from Github runner is received and added to our wstunnel command.
6. Local listeners are stopped. 
7. Start wstunnel and background
8. Create wireguard interface from provided config
9. The workflow will automatically stop after its maximum lifetime of 6 hours. 

### Expected output
```bash
python start.py
Starting local listener...
Starting workflow...
Workflow started!
Waiting for remote url...
Starting listener on port 55278


[Interface]
PrivateKey = SAgU4m8T6ZsMWzMWMOurHzLas3212Sw7CJiHzW2c5mo=
ListenPort = 52820
Address = 10.0.0.2/32
DNS = 1.1.1.1
MTU = 1200

[Peer]
PublicKey = KPRhqXXHUmtqKL+D/+NiKCIkKdjbrc/8rXaETJsA33w=
PresharedKey = 5dejphnQf6aaLv7xOb36nojgOPZLilxubSNuVrGzHpw=
AllowedIPs = 10.0.0.1/32
Endpoint = 127.0.0.1:51820



wstunnel client -L 'udp://127.0.0.1:51820:127.0.0.1:51820?timeout_sec=0' wss://rental-defining-gift-fda.trycloudflare.com
Killing local listener
```

### Provided files
All of the required repository files are located within the `workflow_repo_files` folder in this repository. Either add these to an existing repository of yours or create a new one. No additonal files needed. 
