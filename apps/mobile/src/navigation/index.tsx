import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { HomeScreen } from '../screens/HomeScreen';
// import { DetectionInputScreen } from '../screens/DetectionInputScreen';
// import { AnalysisScreen } from '../screens/AnalysisScreen';
// import { ResultScreen } from '../screens/ResultScreen';

const Stack = createNativeStackNavigator();

export function RootNavigator() {
  return (
    <Stack.Navigator screenOptions={{ headerShown: false }}>
      <Stack.Screen name="Home" component={HomeScreen} />
      {/* <Stack.Screen name="DetectionInput" component={DetectionInputScreen} />
      <Stack.Screen name="Analysis" component={AnalysisScreen} />
      <Stack.Screen name="Result" component={ResultScreen} /> */}
    </Stack.Navigator>
  );
}