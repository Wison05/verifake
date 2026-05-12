import React, { useEffect, useState } from 'react';
import { View, Text } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { styles } from './AnalysisScreen.styles';
import { ClipboardDocumentCheckIcon } from 'react-native-heroicons/outline';
import { BottomNavigation } from '../components/BottomNavigaton';

type StepStatus = 'done' | 'loading' | 'wait';

const STEPS = [
    '영상을 서버로 보내는 중',
    '영상 파일 불러오는 중',
    'AI가 영상을 분석하는 중',
    '분석 완료!',
];

function getScreenText(activeStep: number): { title: string; subTitle: string } {
    switch (activeStep) {
        case 1: return { title: '영상을 보내는 중이에요', subTitle: '잠깐만 기다려 주세요' };
        case 2: return { title: '영상을 불러오는 중이에요', subTitle: '서버에서 영상을 준비하고 있어요' };
        case 3: return { title: 'AI가 분석하고 있어요', subTitle: '딥페이크 여부를 꼼꼼히 살펴보고 있어요' };
        case 4: return { title: '분석이 끝났어요!', subTitle: '결과를 확인해 보세요' };
        default: return { title: '분석 중이에요', subTitle: '잠깐만 기다려 주세요' };
    }
}

function getStepStatus(stepNumber: number, activeStep: number): StepStatus {
    if (stepNumber < activeStep) return 'done';
    if (stepNumber === activeStep) return 'loading';
    return 'wait';
}

export const AnalysisScreen = ({ navigation, route }: any) => {
    const [activeStep, setActiveStep] = useState(1);
    const { thumbnailUri } = route.params || {};
    const { title, subTitle } = getScreenText(activeStep);

    useEffect(() => {
        let isMounted = true;

        // TODO: 백엔드 연결 후 실제 API 호출로 교체
        async function runMockAnalysis() {
            for (let step = 1; step <= 4; step++) {
                if (!isMounted) return;
                setActiveStep(step);
                await new Promise((resolve) => setTimeout(resolve, 750));
            }
            if (isMounted) {
                navigation.navigate('Result', { thumbnailUri });
            }
        }

        runMockAnalysis();

        return () => {
            isMounted = false;
        };
    }, [navigation, thumbnailUri]);

    return (
        <SafeAreaView style={styles.container}>
            <View style={styles.content}>
                <View style={styles.loaderContainer}>
                    <View style={styles.outerCircle}>
                        <View style={styles.innerCircle}>
                            <ClipboardDocumentCheckIcon size={40} color="#7c6cfa" strokeWidth={2} />
                        </View>
                    </View>
                    <Text style={styles.title}>{title}</Text>
                    <Text style={styles.subTitle}>{subTitle}</Text>
                </View>

                <View style={styles.stepList}>
                    {STEPS.map((label, index) => {
                        const stepNumber = index + 1;
                        const status = getStepStatus(stepNumber, activeStep);
                        return (
                            <View key={stepNumber} style={[styles.stepItem, status === 'done' ? styles.stepDone : styles.stepWait]}>
                                <View style={[styles.checkCircle, status === 'done' && styles.checkCircleDone]}>
                                    {status === 'done' && <Text style={styles.checkIcon}>✓</Text>}
                                    {status === 'loading' && <Text style={styles.loadingIcon}>…</Text>}
                                </View>
                                <Text style={[styles.stepLabel, status === 'done' && styles.textDone]}>
                                    {label}
                                </Text>
                            </View>
                        );
                    })}
                </View>
            </View>

            <BottomNavigation navigation={navigation} activeRoute="DetectionInput" />
        </SafeAreaView>
    );
};
