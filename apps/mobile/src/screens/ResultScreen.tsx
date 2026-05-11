import React from 'react';
import { View, Text, ScrollView, TouchableOpacity, Image } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { ArrowLeftIcon } from 'react-native-heroicons/outline';
import { styles } from './ResultScreen.styles';
import { BottomNavigation } from '../components/BottomNavigaton';
import type { MediaTaskResult } from '../api/verifakeApi';

interface ResultRouteParams {
    separatedMedia?: MediaTaskResult;
    thumbnailUri?: string | null;
}

export const ResultScreen = ({ navigation, route }: any) => {
    const { separatedMedia, thumbnailUri } = (route.params || {}) as ResultRouteParams;

    // TODO: 실제 AI 분석 결과로 교체 예정
    const analysisResult = {
        deepfakeScore: 87,
        isFake: true,
        summary: '이 영상에서 두 가지 이상한 점이 발견되었습니다.',
        details: [
            '첫째, 영상에서 얼굴이 교체된 흔적이 있습니다. 특히 3분 12초~18초 구간에서 얼굴 윤곽이 자연스럽지 않게 처리된 것으로 보입니다.',
            '둘째, 음성에서도 편집된 흔적이 감지되었습니다. 2분 45초 구간에서 음성이 이어붙인 것처럼 들립니다.',
        ],
        warning: '! 영상 화질 문제로 일부 구간은 정확한 분석이 어려웠습니다.',
    };

    const { isFake, deepfakeScore } = analysisResult;

    return (
        <SafeAreaView style={styles.container}>
            <View style={styles.header}>
                <TouchableOpacity onPress={() => navigation.navigate('Home')} style={styles.backBtn}>
                    <ArrowLeftIcon size={24} color="#7c6cfa" />
                </TouchableOpacity>
                <Text style={styles.headerTitle}>분석 결과</Text>
                <View style={{ width: 24 }} />
            </View>

            <ScrollView contentContainerStyle={styles.body}>
                {/* 썸네일 + 판정 배지 */}
                <View style={styles.mediaPreview}>
                    {thumbnailUri ? (
                        <Image source={{ uri: thumbnailUri }} style={styles.previewImage} resizeMode="cover" />
                    ) : (
                        <View style={[styles.previewImage, { backgroundColor: '#0a0a0f' }]} />
                    )}
                    <View style={{ position: 'absolute', top: 16, right: 16 }}>
                        <View style={[styles.statusBadge, isFake ? styles.bgFake : styles.bgReal]}>
                            <Text style={styles.statusBadgeText}>{isFake ? 'FAKE' : 'REAL'}</Text>
                        </View>
                    </View>
                </View>

                {/* 딥페이크 가능성 수치 + 게이지 */}
                <Text style={styles.mainResultTitle}>딥페이크 가능성: {deepfakeScore}%</Text>
                <View style={[styles.gaugeBar, { marginBottom: 24 }]}>
                    <View style={[styles.gaugeFill, { width: `${deepfakeScore}%` }, isFake ? styles.bgFake : styles.bgReal]} />
                </View>

                {/* 분석 요약 카드 */}
                <View style={styles.anomalySection}>
                    <Text style={styles.anomalySubTitle}>{analysisResult.summary}</Text>
                    {analysisResult.details.map((text, i) => (
                        <Text key={i} style={[styles.anomalyText, { marginBottom: 12 }]}>{text}</Text>
                    ))}
                    <Text style={styles.limitTitle}>{analysisResult.warning}</Text>
                </View>

                {/* 상세 보고서 버튼 */}
                <TouchableOpacity
                    style={styles.primaryButton}
                    onPress={() => navigation.navigate('ResultDetail', { separatedMedia })}
                >
                    <Text style={styles.primaryButtonText}>상세 분석 보고서 확인하기</Text>
                </TouchableOpacity>

                <View style={{ height: 20 }} />
            </ScrollView>

            <BottomNavigation navigation={navigation} activeRoute="DetectionInput" />
        </SafeAreaView>
    );
};
