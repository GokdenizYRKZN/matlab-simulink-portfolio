import socket
import select

# ArduPilot'un PWM'lerini dinleyecek soket
ardupilot_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
ardupilot_sock.bind(('127.0.0.1', 9002)) 

# Simulink'in JSON paketlerini dinleyecek soket
simulink_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
simulink_sock.bind(('127.0.0.1', 9003)) 

SIMULINK_RX_PORT = 9004
ardupilot_addr = None

print("HIL Koprusu Aktif! Veri akisi bekleniyor...")

while True:
    # Veri gelene kadar CPU'yu yormadan bekle
    readable, _, _ = select.select([ardupilot_sock, simulink_sock], [], [])
    
    for sock in readable:
        if sock is ardupilot_sock:
            # ArduPilot'tan gelen Binary PWM paketini yakala
            pwm_data, addr = sock.recvfrom(1024)
            ardupilot_addr = addr # Gizli portu (ornek: 62898) kaydet
            # Binary paketi Simulink'e yonlendir
            ardupilot_sock.sendto(pwm_data, ('127.0.0.1', SIMULINK_RX_PORT))
            
        elif sock is simulink_sock:
            # Simulink'ten gelen JSON paketini yakala
            json_data, _ = sock.recvfrom(2048)
            if ardupilot_addr:
                # JSON metnini ArduPilot'un ogrenilen gizli portuna firlat
                simulink_sock.sendto(json_data, ardupilot_addr)