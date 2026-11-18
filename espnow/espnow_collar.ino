/* ==========================================================================
 * 嘉蘭 1號 / 2號 — ESP-NOW 對講測試
 * --------------------------------------------------------------------------
 * 來源：Learn ESP32 第 14 課「板對板通訊」（模擬器實跑驗證過）
 *       https://learn-esp32.vercel.app/
 * 改動：把 A/B 改標成嘉蘭1號/2號、加註頸圈實務注意事項。
 *
 * 實測結果（瀏覽器模擬器，10 m 直視）：
 *   A(嘉蘭1號) 24:6F:28:A1:3C:5D
 *   B(嘉蘭2號) 24:6F:28:B2:4C:10
 *   雙向收發正常，RSSI -60 ~ -64 dBm
 *
 * ⚠ 這是模擬器結果。實機在室內（牆 + 人體吸收）通常會再掉 10–20 dB。
 * ========================================================================== */
#include <WiFi.h>
#include <esp_now.h>

// 廣播位址：同一個程式燒進兩塊板，不用各自記對方的 MAC
uint8_t everyone[] = {0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF};

const int BUTTON = 0;   // BOOT（嘉蘭1號：主人輕按；2號：配戴端）
const int LED    = 2;   // 板上藍色 LED
bool lit  = false;
bool last = false;

// 每收到一條訊息就執行
void onReceive(const esp_now_recv_info_t* info, const uint8_t* data, int len) {
  digitalWrite(LED, data[0]);
  Serial.printf("Got %d (%d dBm)\n", data[0], info->rx_ctrl->rssi);
}

void setup() {
  Serial.begin(115200);
  pinMode(BUTTON, INPUT_PULLUP);
  pinMode(LED, OUTPUT);
  WiFi.mode(WIFI_STA);           // ESP-NOW 走 Wi-Fi 射頻，不是 BLE
  Serial.println(WiFi.macAddress());

  esp_now_init();
  esp_now_register_recv_cb(onReceive);

  esp_now_peer_info_t peer = {};
  memcpy(peer.peer_addr, everyone, 6);
  esp_now_add_peer(&peer);
}

void loop() {
  bool now = digitalRead(BUTTON) == LOW;
  if (now && !last) {
    lit = !lit;
    esp_now_send(everyone, (uint8_t*)&lit, 1);
    Serial.printf("Sent %d\n", lit);
    delay(30);                   // 去彈跳
  }
  last = now;
}

/* --------------------------------------------------------------------------
 * 若要用在真的嘉蘭頸圈上，這支範例要改三件事：
 *
 * 1) 不要用廣播。
 *    量產要記對方 MAC（配對時交換），否則附近任何 ESP-NOW 裝置都收得到你的狀態。
 *
 * 2) 加通道鎖定。
 *    esp_now_set_pmk() + peer.channel = 固定頻道，避免跳頻時漏封包。
 *    （廣播模式下必須鎖 channel，否則每次換頻道都要重送）
 *
 * 3) 功耗。
 *    WiFi 射頻開著比 BLE 耗電一個量級。頸圈要 2.5 天續航，
 *    正確做法是「BLE 當常態、ESP-NOW 只在配對或大量傳輸時短暫開啟」。
 * -------------------------------------------------------------------------- */
