import React, { useEffect, useState } from 'react';
import { Alert, View, Text, SafeAreaView } from 'react-native';
import { styles } from './AnalysisScreen.styles';
import { ClipboardDocumentCheckIcon } from 'react-native-heroicons/outline';
import { BottomNavigation } from '../components/BottomNavigaton';
import { collectInstagramVideo, uploadVideoForSeparation, waitForMediaSeparation } from '../api/verifakeApi';

type StepStatus = 'done' | 'loading' | 'wait' | 'error';

interface SeparationStep {
    id: number;
    label: string;
    status: StepStatus;
}

function buildSteps(activeStep: number, hasError: boolean): SeparationStep[] {
    const labels = [
        '서버로 영상 전달',
        'ffmpeg 영상/음성 분리',
        '분리 결과 경로 확인',
        '서버 AI 실행 없음',
    ];

    return labels.map((label, index) => {
        const stepNumber = index + 1;
        if (hasError && stepNumber === activeStep) {
            return { id: stepNumber, label, status: 'error' };
        }
        if (stepNumber < activeStep) {
            return { id: stepNumber, label, status: 'done' };
        }
        if (stepNumber === activeStep) {
            return { id: stepNumber, label, status: 'loading' };
        }
        return { id: stepNumber, label, status: 'wait' };
    });
}

export const AnalysisScreen = ({ navigation, route }: any) => {
    const [activeStep, setActiveStep] = useState(1);
    const [hasError, setHasError] = useState(false);
    const { videoUri, thumbnailUri, url } = route.params || {};
    const steps = buildSteps(activeStep, hasError);

    useEffect(() => {
        let isMounted = true;

        async function runSeparationRequest() {
            try {
                setActiveStep(1);
                const submittedTask = typeof videoUri === 'string' && videoUri.length > 0
                    ? await uploadVideoForSeparation(videoUri)
                    : await collectInstagramVideo(String(url ?? ''));

                if (!isMounted) {
                    return;
                }

                setActiveStep(2);
                const separatedMedia = await waitForMediaSeparation(submittedTask.task_id);

                if (!isMounted) {
                    return;
                }

                setActiveStep(4);
                navigation.navigate('Result', { separatedMedia, thumbnailUri });
            } catch (error) {
                if (!isMounted) {
                    return;
                }
                setHasError(true);
                const message = error instanceof Error ? error.message : '영상/음성 분리에 실패했습니다.';
                Alert.alert('분리 실패', message, [
                    { text: '다시 선택하기', onPress: () => navigation.navigate('DetectionInput') },
                ]);
            }
        }

        runSeparationRequest();

        return () => {
            isMounted = false;
        };
    }, [navigation, thumbnailUri, url, videoUri]);

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
                    <Text style={styles.title}>영상/음성 분리 중</Text>
                    <Text style={styles.subTitle}>서버에서는 AI 없이 미디어 분리만 수행합니다</Text>
                </View>

                {/* 분석 단계 리스트 */}
                <View style={styles.stepList}>
                    {steps.map((step) => (
                        <View key={step.id} style={[styles.stepItem, step.status === 'done' ? styles.stepDone : styles.stepWait]}>
                            <View style={[styles.checkCircle, step.status === 'done' && styles.checkCircleDone, step.status === 'error' && styles.checkCircleError]}>
                                {step.status === 'done' && <Text style={styles.checkIcon}>✓</Text>}
                                {step.status === 'loading' && <Text style={styles.loadingIcon}>…</Text>}
                                {step.status === 'error' && <Text style={styles.checkIcon}>!</Text>}
                            </View>
                            <Text style={[styles.stepLabel, step.status === 'done' && styles.textDone, step.status === 'error' && styles.textError]}>
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
