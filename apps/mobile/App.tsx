import './global.css';
import { useEffect } from "react";
import { useShareIntent } from "expo-share-intent";
import { NavigationContainer, createNavigationContainerRef } from '@react-navigation/native';
import { RootNavigator } from './src/navigation';

export const navigationRef = createNavigationContainerRef();

export default function App() {
  const { hasShareIntent, shareIntent, resetShareIntent } = useShareIntent();

  // 공유 데이터가 있을 경우 처리
  useEffect(() => {
    const sharedUrl = shareIntent.text || (shareIntent as any).value;

    if (hasShareIntent && sharedUrl && navigationRef.isReady()) {
      console.log("공유받은 URL 처리 중:", sharedUrl);

      (navigationRef as any).navigate('DetectionInput', {
        sharedUrl: sharedUrl
      });

      resetShareIntent();
    }
  }, [hasShareIntent, shareIntent]);

  return (
    <NavigationContainer ref={navigationRef}>
      <RootNavigator />
    </NavigationContainer>
  );
}