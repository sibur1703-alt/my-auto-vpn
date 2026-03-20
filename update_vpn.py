import requests
import urllib.parse
import yaml

# --- МАГИЯ: Заставляем YAML всегда ставить кавычки ---
class QuotedStr(str): pass

def quoted_scalar(dumper, data):
    return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='"')

yaml.add_representer(QuotedStr, quoted_scalar)
# -----------------------------------------------------

def parse_vless(url):
    url = url.strip()
    if not url.startswith('vless://'): return None
    try:
        main_part, name_encoded = url.split('#', 1) if '#' in url else (url, "Unnamed")
        name = urllib.parse.unquote(name_encoded)
        main_part = main_part.replace('vless://', '')
        auth_server, params_str = main_part.split('?', 1) if '?' in main_part else (main_part, "")
        uuid, server_port = auth_server.split('@', 1)
        server, port = server_port.split(':', 1)
        params = dict(urllib.parse.parse_qsl(params_str))
        
        proxy = {"name": name, "type": "vless", "server": server, "port": int(port), "uuid": uuid, "udp": True}
        if params.get("security") in ["tls", "reality"]:
            proxy["tls"] = True
            proxy["servername"] = params.get("sni", server)
            if params.get("fp"): proxy["client-fingerprint"] = params.get("fp")
        
        if params.get("security") == "reality":
            sid = params.get("sid", "")
            if sid:
                if len(sid) > 16 or len(sid) % 2 != 0 or not all(c in '0123456789abcdefABCDEF' for c in sid):
                    return None 
                # Оборачиваем short-id в нашу защиту, чтобы всегда были кавычки
                proxy["reality-opts"] = {"public-key": params.get("pbk", ""), "short-id": QuotedStr(sid)}
            else:
                proxy["reality-opts"] = {"public-key": params.get("pbk", "")}
        
        net_type = params.get("type", "tcp")
        proxy["network"] = net_type
        if net_type == "ws":
            proxy["ws-opts"] = {"path": params.get("path", "/"), "headers": {"Host": params.get("host", params.get("sni", server))}}
        elif net_type == "grpc":
            proxy["grpc-opts"] = {"grpc-service-name": params.get("serviceName", "")}
        return proxy
    except: return None

def main():
    print("🔄 Скачиваем свежие конфиги...")
    url = "https://raw.githubusercontent.com/AvenCores/goida-vpn-configs/main/githubmirror/26.txt"
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        lines = resp.text.splitlines()
    except Exception as e:
        print(f"❌ Ошибка скачивания: {e}")
        return

    proxies = []
    names = []
    for line in lines:
        p = parse_vless(line)
        if p:
            orig_name = p["name"]
            c = 1
            while p["name"] in names:
                p["name"] = f"{orig_name} {c}"
                c += 1
            proxies.append(p)
            names.append(p["name"])

    if not proxies:
        print("⚠️ Нет валидных серверов!")
        return

    clash_config = {
        "proxies": proxies,
        "proxy-groups": [{
            "name": "🚀 Авто-выбор (URL-Test)",
            "type": "url-test",
            "proxies": names,
            "url": "http://cp.cloudflare.com/generate_204",
            "interval": 300,
            "tolerance": 50
        }],
        "rules": ["MATCH,🚀 Авто-выбор (URL-Test)"]
    }

    with open("flclash_config.yaml", "w", encoding="utf-8") as f:
        yaml.dump(clash_config, f, allow_unicode=True, sort_keys=False)
    print(f"✅ Готово! Сконвертировано серверов: {len(proxies)}")

if __name__ == "__main__":
    main()
