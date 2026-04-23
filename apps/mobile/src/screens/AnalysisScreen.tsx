import React, { useEffect, useState } from 'react';
import { View, Text, SafeAreaView, Animated } from 'react-native';
import { styles } from './AnalysisScreen.styles';
import { ClipboardDocumentCheckIcon } from 'react-native-heroicons/outline';
import { BottomNavigation } from '../components/BottomNavigaton';

export const AnalysisScreen = ({ navigation, route }: any) => {
    const [progress, setProgress] = useState(0);
    const { selectedVideo } = route.params || {};

    // 분석 단계들
    const steps = [
        { id: 1, label: '영상 프레임 추출', status: 'done' },
        { id: 2, label: 'ViT 모델 추론', status: 'done' },
        { id: 3, label: '음성 패턴 분석', status: 'loading' },
        { id: 4, label: 'LLM 설명 생성', status: 'wait' },
    ];

    useEffect(() => {
        // 임시 타이머
        const timer = setTimeout(() => {
            navigation.navigate('Result', { videoUri: selectedVideo });
        }, 5000);
        return () => clearTimeout(timer);
    }, [navigation]);

    return (
        <SafeAreaView style={styles.container}>
            <View style={styles.content}>
                {/* 중앙 */}
                <View style={styles.loaderContainer}>
                    <View style={styles.outerCircle}>
                        <View style={styles.innerCircle}>
                            <ClipboardDocumentCheckIcon size={40} color="#7c6cfa" strokeWidth={2} />
                        </View>
                    </View>
                    <Text style={styles.title}>영상 분석 중</Text>
                    <Text style={styles.subTitle}>약 15~30초 소요됩니다</Text>
                </View>

                {/* 분석 단계 리스트 */}
                <View style={styles.stepList}>
                    {steps.map((step) => (
                        <View key={step.id} style={[styles.stepItem, step.status === 'done' ? styles.stepDone : styles.stepWait]}>
                            <View style={[styles.checkCircle, step.status === 'done' && styles.checkCircleDone]}>
                                {step.status === 'done' && <Text style={styles.checkIcon}>✓</Text>}
                            </View>
                            <Text style={[styles.stepLabel, step.status === 'done' && styles.textDone]}>
                                {step.label}
                            </Text>
                        </View>
                    ))}
                </View>
            </View>

            <BottomNavigation navigation={navigation} activeRoute="DetectionInput" />
        </SafeAreaView>
    );
};