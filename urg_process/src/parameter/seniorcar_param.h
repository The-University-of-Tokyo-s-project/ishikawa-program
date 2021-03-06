const float SENIORCAR_WHEEL_BASE_LENGTH = 0.9;
const float SENIORCAR_TREAD_LENGTH = 0.57;
const float SENIORCAR_HARF_TREAD_LENGTH = SENIORCAR_TREAD_LENGTH / 2.0;

//const float SENIORCAR_WHEEL_RADIUS = 0.13;
//const float SENIORCAR_WHEEL_THICKNESS = 0.08;

const float SENIORCAR_WHEEL_RADIUS = 0.15;
const float SENIORCAR_WHEEL_THICKNESS = 0.10;

const float SENIORCAR_COG_HEIGHT = 0.6;
const float GRVITY_ACCELERATION = 9.806;

const float SENIORCAR_FULL_LENGTH = 1.18;
const float SENIORCAR_FULL_WIDTH  = 0.65;
const float SENIORCAR_FULL_HEIGHT = 1.08;

const float SENIORCAR_DANGER_ZMP_POS_Y = SENIORCAR_HARF_TREAD_LENGTH;
const float SENIORCAR_TIRE_MOVABLE_LENGHT = 0.08;

//const float SENIORCAR_FRONT_SPRING_CONSTANT = 12000;
const float SENIORCAR_FRONT_SPRING_CONSTANT = 13960;
//const float SENIORCAR_BACK_SPRING_CONSTANT  = 38000;
//const float SENIORCAR_BACK_SPRING_CONSTANT  = 138000;
const float SENIORCAR_BACK_SPRING_CONSTANT = 30459 * 2;

const float SENIORCAR_WEIGHT = 100 + 70; // 車両重量＋人
const float SENIORCAR_ROLL_MOMENT_OF_INERTIA = 15.6;

//const float SENIORCAR_DRIVABLE_STEP_HEIGHT = 0.075; // 乗り越え可能段差高さ（カタログ値）
const float SENIORCAR_DRIVABLE_STEP_HEIGHT = 0.1; // 調整値

const int PREDEICT_FRONT_INDEX = 73;