// 一周10000パルス
int MAX_ROT_ANGLE = 30000;
int MIN_ROT_ANGLE = -100;
int STOP_THRESHOLD = 100;

// モーター関連ピン
int FWD = 6;
int BRK = 7;
int RWD = 8;

// ロータリーエンコーダーの配線に合わせる
int dRotAPin  = 2;
int dRotBPin  = 4;
int dRotZPin  = 3;
int R_count   = 0;
// ロータリーエンコーダーの状態を記憶する
// 割り込み中に変化する変数はvolatileをつけて宣言する
volatile int m_nOldRot = 0;
volatile long m_nValue  = 0L;

boolean rev_right = true;
boolean loop_mode = true;
 
void setup()
{
  // ピンの設定
  pinMode(FWD,OUTPUT);
  pinMode(BRK,OUTPUT); 
  pinMode(RWD,OUTPUT);
  // INPUTモードにします。
  pinMode(dRotAPin, INPUT);
  pinMode(dRotBPin, INPUT);
  pinMode(dRotZPin, INPUT);
 
  // プルアップを有効にします
  digitalWrite(dRotAPin, HIGH);
  digitalWrite(dRotBPin, HIGH);
  digitalWrite(dRotZPin, HIGH);
 
  // 外部割り込みを設定します
  // D2ピンが 変化 した時にrotRotEnd()を呼び出します
  attachInterrupt(0, rotRotEnc, CHANGE);
  //シリアル通信速度を設定します
  Serial.begin(9600);
}
 
void loop()
{
  // シリアル通信に"e"が来てたら終了
  if( Serial.available() > 0){
    char recive = Serial.read();
    if( recive == 's'){
      loop_mode = true;
    }
    else if(recive == 'e'){
      loop_mode = false;
    }
  }
  
  // 周期的に回転させる処理
  if(loop_mode){
    Serial.println(m_nValue);
     if(m_nValue > MAX_ROT_ANGLE){
      rev_right = false;
    }
    else if(m_nValue < MIN_ROT_ANGLE){
      rev_right = true;
    }
    if(rev_right){
      revRight();
    }
    else{
      revLeft();
    }
    delay(30);
  }
  // 回転角度を0に戻す処理
  else{
    if(m_nValue > STOP_THRESHOLD){
      revLeft();
    }
    else if( m_nValue < -STOP_THRESHOLD ){
      revRight();
    }
    else{
      revStop();
    }
    delay(5);
  }
  
}

void revRight(){
  digitalWrite(FWD,LOW);
  digitalWrite(RWD,HIGH);
  digitalWrite(BRK,LOW);
}

void revLeft(){
  digitalWrite(FWD,HIGH);
  digitalWrite(RWD,LOW);
  digitalWrite(BRK,LOW);
}

void revStop(){
  digitalWrite(FWD,LOW);
  digitalWrite(RWD,LOW);
  digitalWrite(BRK,HIGH);
}

// 外部割り込みから呼び出される変数
void rotRotEnc(void)
{
  int valA = PIND & _BV(2);
  int valB = PIND & _BV(4);
  
  if(!valA){  // ロータリーエンコーダー回転開始
    if(valB){
      //右回転
      m_nOldRot = 1;
    } else {
      //左回転
      m_nOldRot = -1;
    }
  } else {  // ロータリーエンコーダー回転停止
    if(valB){
      if(m_nOldRot == -1){
        // 左回転の時の処理
        m_nValue--;
      }
    } else {
      if(m_nOldRot == 1){
        //右回転の時の処理
        m_nValue++;
      }
    }
    // ここでロータリーエンコーダーの状態をクリア
    m_nOldRot = 0;
  }
}
