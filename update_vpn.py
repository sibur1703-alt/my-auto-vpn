import requests

def main():
    print("🚀 Запускаем сборщик сырых VLESS-ссылок...")
    
    # === ТВОИ ССЫЛКИ ===
    # Сюда можешь вставлять любые raw-ссылки через запятую.
    urls = [
        "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/main/WHITE-CIDR-RU-checked.txt",
        "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/refs/heads/main/WHITE-CIDR-RU-all.txt",
        "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/refs/heads/main/WHITE-SNI-RU-all.txt",
        "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/refs/heads/main/Vless-Reality-White-Lists-Rus-Mobile.txt",
        "https://raw.githubusercontent.com/barry-far/V2ray-config/main/Splitted-By-Protocol/vless.txt",
                # "https://raw.githubusercontent.com/кто-то/еще/main/vless.txt",
    ]
    
    # Используем set (множество) - оно автоматически удаляет дубликаты ссылок
    vless_links = set() 
    
    for url in urls:
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                lines = resp.text.splitlines()
                count = 0
                for line in lines:
                    line = line.strip()
                    # Ищем только строчки, которые начинаются с vless://
                    if line.startswith('vless://'):
                        vless_links.add(line)
                        count += 1
                filename = url.split('/')[-1]
                print(f"✅ Скачано {count} ссылок из: {filename}")
            else:
                print(f"⚠️ Ошибка {resp.status_code} для ссылки: {url}")
        except Exception as e:
            print(f"❌ Ошибка скачивания {url}: {e}")
    
    if not vless_links:
        print("⚠️ Ни одной vless-ссылки не найдено!")
        return
        
    # Сохраняем всё в обычный текстовый файл
    with open("my_vless_collection.txt", "w", encoding="utf-8") as f:
        for link in vless_links:
            f.write(link + "\n")
            
    print(f"\n🎉 ГОТОВО! Сохранено уникальных ссылок: {len(vless_links)}")

if __name__ == "__main__":
    main()
