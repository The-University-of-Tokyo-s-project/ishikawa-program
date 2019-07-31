#include "accident_predictor_for_penetration_voxel_map_test.h"

AccidentPredictor::AccidentPredictor(float pos_x,float pos_y,float pos_z) : PenetrationVoxelMap(pos_x,pos_y,pos_z)
{
	predicted_path.resize(DEG_CALCULTE_NUM);
	for(int i=0; i < DEG_CALCULTE_NUM; i++){
		predicted_path[i].resize(PATH_POINT_NUM);
	}
	for(int i=0; i < DEG_CALCULTE_NUM; i++){
		for(int j=0; j < PATH_POINT_NUM; j++){
			predicted_path[i][j].resize(3);
		}
	}

	// タイヤの内どこで何を計算するかを計算しておく
	const double TIRE_X_SPLIT_NUM = 2;
	const double TIRE_Y_SPLIT_NUM = 1;
	const double TIRE_CALC_MARGINE = 0.01;
	tire_calculation_point.resize( ( TIRE_X_SPLIT_NUM * 2 + 1 ) * (TIRE_Y_SPLIT_NUM * 2 + 1));
	for(int i=0; i < ( TIRE_X_SPLIT_NUM * 2 + 1 ) * (TIRE_Y_SPLIT_NUM * 2 + 1) ;i++){
		tire_calculation_point[i].resize(3);
	}
	for(int i=0; i < TIRE_X_SPLIT_NUM * 2 + 1 ; i++){
		for(int j=0; j < TIRE_Y_SPLIT_NUM * 2 + 1 ; j++){
			int tire_calc_index = i*( TIRE_Y_SPLIT_NUM * 2 + 1 ) + j ;
			tire_calculation_point[tire_calc_index][0] = ( (SENIORCAR_WHEEL_RADIUS - TIRE_CALC_MARGINE) / TIRE_X_SPLIT_NUM ) * ( i - TIRE_X_SPLIT_NUM );
			tire_calculation_point[tire_calc_index][1] = ( SENIORCAR_WHEEL_THICKNESS / ( TIRE_Y_SPLIT_NUM * 2 ) ) * ( j - TIRE_Y_SPLIT_NUM );
			tire_calculation_point[tire_calc_index][2] = -sqrt( pow(SENIORCAR_WHEEL_RADIUS,2) - pow(tire_calculation_point[tire_calc_index][0],2));
			//cout << "tire_index:" << tire_calc_index << " x:" << tire_calculation_point[tire_calc_index][0] << " y:" << tire_calculation_point[tire_calc_index][1] << " z:" << tire_calculation_point[tire_calc_index][2] << endl;
		}
	}

	// タイヤのパラメータから計算するボクセルを算出
	int tire_radius_in_grid =  SENIORCAR_WHEEL_RADIUS / HORIZONTAL_RESOLUTION;
	int tire_half_width_in_grid = SENIORCAR_WHEEL_THICKNESS / ( HORIZONTAL_RESOLUTION * 2.0 );
	if(tire_half_width_in_grid==0){ tire_half_width_in_grid = 1; }
	if(tire_radius_in_grid==0){ tire_radius_in_grid = 1; }
	tire_radius_in_grid = 1;
	tire_half_width_in_grid = 0;
	tire_calculation_index.resize( ( tire_half_width_in_grid * 2 + 1 ) * ( tire_radius_in_grid * 2 + 1) );
	for(int i=0; i < ( tire_half_width_in_grid * 2 + 1 ) * ( tire_radius_in_grid * 2 + 1); i++){
		tire_calculation_index[i].resize(3);
	}

	for(int i=0; i < tire_half_width_in_grid * 2 + 1; i++){
		for(int j=0; j < tire_radius_in_grid * 2 + 1; j++){
			int tire_calc_index = i * ( tire_radius_in_grid * 2 + 1 ) + j ;
			tire_calculation_index[tire_calc_index][0] = j - tire_radius_in_grid;
			tire_calculation_index[tire_calc_index][1] = i - tire_half_width_in_grid;
			float calc_height = sqrt( pow(SENIORCAR_WHEEL_RADIUS,2) - pow( HORIZONTAL_RESOLUTION * float(abs(tire_calculation_index[tire_calc_index][0])),2) );
			tire_calculation_index[tire_calc_index][2] = -calc_height / VERTICAL_RESOLUTION;
			cout << tire_calculation_index[tire_calc_index][0] << "," << tire_calculation_index[tire_calc_index][1] << "," << tire_calculation_index[tire_calc_index][2] << endl;
		}
	}

	// 定数計算
	C_f = SENIORCAR_FRONT_SPRING_CONSTANT * SENIORCAR_TREAD_LENGTH * 0.5 / ( 0.5 * ( SENIORCAR_FRONT_SPRING_CONSTANT + SENIORCAR_BACK_SPRING_CONSTANT ) * SENIORCAR_TREAD_LENGTH * SENIORCAR_TREAD_LENGTH - SENIORCAR_WEIGHT*9.8*SENIORCAR_COG_HEIGHT) ;
	C_b = SENIORCAR_BACK_SPRING_CONSTANT  * SENIORCAR_TREAD_LENGTH * 0.5 / ( 0.5 * ( SENIORCAR_FRONT_SPRING_CONSTANT + SENIORCAR_BACK_SPRING_CONSTANT ) * SENIORCAR_TREAD_LENGTH * SENIORCAR_TREAD_LENGTH - SENIORCAR_WEIGHT*9.8*SENIORCAR_COG_HEIGHT) ;
	C_a = SENIORCAR_WEIGHT  / ( 0.5 * ( SENIORCAR_FRONT_SPRING_CONSTANT + SENIORCAR_BACK_SPRING_CONSTANT ) * SENIORCAR_TREAD_LENGTH * SENIORCAR_TREAD_LENGTH - SENIORCAR_WEIGHT*9.8*SENIORCAR_COG_HEIGHT) ;

	// 乱数の初期化
	unsigned int    now = (unsigned int)time( 0 );
    //printf( "乱数の種を現在時刻(%u)で初期化します\n", now );
    srand( now );

}


void AccidentPredictor::predictAccident(float pos_x,float pos_y,float pos_z,float roll,float pitch,float yaw,float vehicle_velocity)
{
	vector < CalculatedVehicleState > reset_array;
	calculated_state_array = reset_array;
	CalculatedVehicleState tmp_calculated_state,tmp_calculated_state_old;

	for(int i=0; i < DEG_CALCULTE_NUM; i++){
		for(int j=1; j < PATH_POINT_NUM; j++){
			tmp_calculated_state.vehicle_pose[2] = pos_z;
			returnTirePositionAtGivenPose(&tmp_calculated_state,predicted_path[i][j]);	// 四輪の接地位置計算
			calculated_state_array.push_back(tmp_calculated_state);
		}
	}

	int index,accident_count;
	for(int i=0; i < DEG_CALCULTE_NUM; i++){
		for(int j=1; j < PATH_POINT_NUM; j++){
			
			index =  j  + ( PATH_POINT_NUM - 1 ) * i ;
			accident_count = 0;

			for(int k=0; k < CALC_LOOP_NUM; k++){

				// 車輪高さ更新
				//randomSamplingTireHeighrByPropanilityDensity(&calculated_state_array[index]);
				//randomSamplingTireHeighrByPropanilityDensity(&calculated_state_array[index-1]);
				mostLikelyTireHeightByPropanilityDensity(&calculated_state_array[index]);
				mostLikelyTireHeightByPropanilityDensity(&calculated_state_array[index-1]);
				
				}
			}
		}
	}

	/*
	index =  PATH_POINT_NUM - 2 + ( PATH_POINT_NUM - 1 ) * DEG_CALCULTE_NUM / 2  ;
	cout << index << "," ;
	printCalculatedState(calculated_state_array[index]);
	*/
	

	//printTireHeightPropabilityDensity();
	
	/*
	CalculatedVehicleState state = calculated_state_array[ PATH_POINT_NUM - 2 + PATH_POINT_NUM * DEG_CALCULTE_NUM / 2 ];
	cout << state.accident_rate << ",pos:" <<  state.vehicle_pose[0] << "," << state.vehicle_pose[1] << "," << state.vehicle_pose[2]
	<< "," << state.calculated_roll_angle  << "," << state.tire_pos[0][2] <<  "," <<  state.tire_pos[1][2] <<  "," <<  state.tire_pos[2][2] <<  "," <<  state.tire_pos[3][2] << endl;  
	*/
	//printTireHeightPropabilityDensity();

	//printFrontLeftTirePropabilityDensity();
	//printPredictedVehicleAngle();
	//printCalculatedState(calculated_state_array[PREDEICT_FRONT_INDEX]);
}


double AccidentPredictor::returnTireHeightAtGivenPositionAndPose(double x_pos,double y_pos,double tire_theta){

	const float START_HEIGHT = -10.0;
	float max_height = START_HEIGHT;
	float tire_pos[2],tire_pos_z;
	//int    tire_pos_index[2];

	for(int i=0; i < tire_calculation_point.size() ;i++){
		tire_pos[0] = x_pos + tire_calculation_point[i][0] * cos(tire_theta) - tire_calculation_point[i][1] * sin(tire_theta);
		tire_pos[1] = y_pos + tire_calculation_point[i][0] * sin(tire_theta) + tire_calculation_point[i][1] * cos(tire_theta);
		//TranslateRealCordinateToIndex(tire_pos_index, tire_pos);
		//tire_pos_z = tire_calculation_point[i][2] + height_map[tire_pos_index[0]][tire_pos_index[1]] ;
		max_height = max(max_height,tire_pos_z);
	}

	return max_height;

}



void AccidentPredictor::calculateSlopeOfVehicle(CalculatedVehicleState *predicted_state){

	int FRONT_LEFT  = 0;
	int FRONT_RIGHT = 1;
	int BACK_LEFT	= 2;
	int BACK_RIGHT	= 3;

	int Z = 2;

	// 新しい実装
	predicted_state->calculated_roll_angle  = C_f * ( predicted_state->tire_pos[FRONT_RIGHT][Z] - predicted_state->tire_pos[FRONT_LEFT][Z] ) + C_b * ( predicted_state->tire_pos[BACK_RIGHT][Z] - predicted_state->tire_pos[BACK_LEFT][Z] ) ;
	predicted_state->calculated_pitch_angle =  -atan( 0.5 * ( predicted_state->tire_pos[FRONT_RIGHT][Z] + predicted_state->tire_pos[FRONT_LEFT][Z] - predicted_state->tire_pos[BACK_RIGHT][Z] - predicted_state->tire_pos[BACK_LEFT][Z] ) / SENIORCAR_WHEEL_BASE_LENGTH );

}


void AccidentPredictor::returnCalculatedVehicleState(visualization_msgs::Marker *triangles){

	triangles->header.frame_id = "/odom";
	triangles->ns = "calculated_state";
	triangles->action = visualization_msgs::Marker::ADD;
	triangles->pose.orientation.w = 1.0;
	triangles->id = 0;
	triangles->type = visualization_msgs::Marker::TRIANGLE_LIST;
	triangles->scale.x = triangles->scale.y = triangles->scale.z = 1.0f;

	geometry_msgs::Point p[3],tmp_p[3];
	std_msgs::ColorRGBA rgba;

	float TRIANGLE_LENGTH = 0.1;
	tmp_p[0].x =  TRIANGLE_LENGTH; tmp_p[0].y =  0.0f;
	tmp_p[1].x = -TRIANGLE_LENGTH; tmp_p[1].y =  TRIANGLE_LENGTH/2.0f; 
	tmp_p[2].x = -TRIANGLE_LENGTH; tmp_p[2].y = -TRIANGLE_LENGTH/2.0f;


	for(int i=0; i < DEG_CALCULTE_NUM; i++){
		for(int j=2; j < PATH_POINT_NUM; j++){
			CalculatedVehicleState tmp_state = calculated_state_array[ j - 1 + ( PATH_POINT_NUM - 1 ) * i ];
			
			rgba.r = 0.0f; rgba.g = 1.0f; rgba.b = 0.0f; rgba.a = 1.0f;
			for(int p_i=0;p_i<3;p_i++){
				float yaw = tmp_state.vehicle_pose[2];
				p[p_i].x = tmp_state.vehicle_pose[0] + cos(yaw) * tmp_p[p_i].x - sin(yaw) * tmp_p[p_i].y;
				p[p_i].y = tmp_state.vehicle_pose[1] + sin(yaw) * tmp_p[p_i].x + cos(yaw) * tmp_p[p_i].y;
				p[p_i].z = 0;
				triangles->points.push_back(p[p_i]);
				triangles->colors.push_back(rgba);
			}
			//cout << tmp_state.vehicle_pose[0] << "," << tmp_state.vehicle_pose[1] << endl;
		}
	}
}


void AccidentPredictor::printTireHeightPropabilityDensity(){

	cout << "print_wheel" <<endl;
		
	//int index =  PATH_POINT_NUM - 2 + PATH_POINT_NUM * DEG_CALCULTE_NUM / 2; // 真正面の方のindex=72~83 0~1.5m
	int index = PREDEICT_FRONT_INDEX;
	CalculatedVehicleState state = calculated_state_array[index];

	
	printCalculatedState(state);

	for(int i=0;i<4;i++){
		for(int j=0;j<3;j++){
			cout <<  fixed << setprecision(3) << state.tire_pos[i][j] << ",";
		}
		cout << "max_height_grid," << returnHighestVoxeclHeightInCordinate(state.tire_pos[i][0],state.tire_pos[i][1]) << ",";
		for(int j=0;j<MAP_SIZE_Z*2;j++){
			cout <<  fixed << setprecision(2) << state.tire_height_probability_density[i][j] << ",";
		}
		cout << endl;
	}

}


void AccidentPredictor::printFrontLeftTirePropabilityDensity(){

	CalculatedVehicleState state = calculated_state_array[PREDEICT_FRONT_INDEX];

	for(int j=0;j<3;j++){
		cout <<  fixed << setprecision(3) << state.tire_pos[0][j] << ",";
	}
	
	cout << "max_height_grid," << returnHighestVoxeclHeightInCordinate(state.tire_pos[0][0],state.tire_pos[0][1]) << ",";
	for(int j=0;j<MAP_SIZE_Z*2;j++){
		cout <<  fixed << setprecision(3) << state.tire_height_probability_density[0][j] << ",";
	}
	
	cout << endl;

}

void AccidentPredictor::printPredictedVehicleAngle(){

	CalculatedVehicleState state = calculated_state_array[PREDEICT_FRONT_INDEX];

	mostLikelyTireHeightByPropanilityDensity(&state);
	calculateSlopeOfVehicle(&state);
	if( abs(state.calculated_roll_angle) < 1.0 && abs(state.calculated_pitch_angle) < 1.0 ){
		cout << state.vehicle_pose[0] << ",;" << state.vehicle_pose[1] << ","  << state.vehicle_pose[2] << ","  << state.vehicle_pose[3] << ", rol:"  << state.calculated_roll_angle  << ", pitch:" << state.calculated_pitch_angle  << endl;
		//printCalculatedState(state);
	}

}


void AccidentPredictor::calculateTireHeightProbabilityDensity(CalculatedVehicleState *return_tire_height){

	int calc_mergine = SENIORCAR_WHEEL_RADIUS / VERTICAL_RESOLUTION + 2;
	int tire_pos_index[2];
	double tmp_propability, tmp_propability_height;
	double propab_sum;

	for(int i=0;i<4;i++){
		tire_pos_index[0] = int( float(MAP_SIZE_X_Y) + ( return_tire_height->tire_pos[i][0] - center_x ) / HORIZONTAL_RESOLUTION );
		tire_pos_index[1] = int( float(MAP_SIZE_X_Y) + ( return_tire_height->tire_pos[i][1] - center_y ) / HORIZONTAL_RESOLUTION );

		for(int j=0; j < calc_mergine; j++){
			return_tire_height->tire_height_probability_density[i][j] = 0;
		}

		propab_sum = 0;
		tmp_propability_height = 1.0; // その高さまでに接地していない確率
		for(int j=MAP_SIZE_Z * 2; j > calc_mergine - 1; j--){
			tmp_propability = 1; // 接地しない確率
			for(int k=0; k < tire_calculation_index.size() ; k++){
				if( voxel_odds_map[tire_pos_index[0] + tire_calculation_index[k][0]][tire_pos_index[1] + tire_calculation_index[k][1]][j + tire_calculation_index[k][2]] > l_0 ){
					tmp_propability *= (1.0 - translateLogOddstoP(voxel_odds_map[tire_pos_index[0] + tire_calculation_index[k][0]][tire_pos_index[1] + tire_calculation_index[k][1]][j + tire_calculation_index[k][2]])) ;
				}
			}
			tmp_propability = 1 - tmp_propability;
			return_tire_height->tire_height_probability_density[i][j] = tmp_propability * tmp_propability_height ;
			propab_sum += return_tire_height->tire_height_probability_density[i][j] ;
			tmp_propability_height *= (1 - tmp_propability);
		}
	}

}

void AccidentPredictor::mostLikelyTireHeightByPropanilityDensity(CalculatedVehicleState *return_tire_height){

	double max_probability = 0.0;
	int max_probab_index = 0;
	int j;

	for(int i=0;i<4;i++){
		max_probability = 0.0;
		max_probab_index = 0;
		for(j=MAP_SIZE_Z * 2-2; j > 0; j--){
			if( return_tire_height->tire_height_probability_density[i][j] > max_probability ){
				max_probability = return_tire_height->tire_height_probability_density[i][j];
				max_probab_index = j;
			}
		}
		return_tire_height->tire_pos[i][2] = float(max_probab_index - MAP_SIZE_Z) * VERTICAL_RESOLUTION + center_z ;
	}

}
