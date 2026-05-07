import React from 'react';
import { View, Text, SafeAreaView, ScrollView, TouchableOpacity } from 'react-native';
import { ChevronLeftIcon } from 'react-native-heroicons/outline';
import Svg, { Circle, G } from 'react-native-svg';
import { styles } from './ResultScreen.styles';

export const ResultDetailScreen = ({ navigation }: any) => {
    //가짜 분석 텍스트 데이터
    const detailData = {
        totalScore: 87,
        confidence: 64,
        matchScore: 71,
        videoScore: 91,
        audioScore: 74,
        videoAnomalies: [
            "L 3:12~3:18 - 얼굴 경계 부자연스러움",
            "L 5:02~5:09 - 눈 깜빡임 패턴 이상"
        ],
        audioAnomalies: [
            "L 2:45~2:51 - 음성 끊김 감지",
            "L 4:30~4:35 - 발화 속도 불규칙"
        ]
    };

    // 원형 그래프 컴포넌트
    const DonutChart = ({ percentage, color, label }: any) => {
        const radius = 35;
        const circumference = 2 * Math.PI * radius;
        const strokeDashoffset = circumference - (percentage / 100) * circumference;

        return (
            <View style={{ alignItems: 'center', flex: 1 }}>
                <Svg width={90} height={90}>
                    <G rotation="-90" origin="45, 45">
                        <Circle cx="45" cy="45" r={radius} stroke="#1e1e2e" strokeWidth="7" fill="none" />
                        <Circle
                            cx="45" cy="45" r={radius} stroke={color} strokeWidth="7" fill="none"
                            strokeDasharray={circumference}
                            strokeDashoffset={strokeDashoffset}
                            strokeLinecap="round"
                        />
                    </G>
                </Svg>
                <View style={{ position: 'absolute', top: 32 }}>
                    <Text style={{ color: '#fff', fontSize: 13, fontWeight: 'bold' }}>{percentage}%</Text>
                </View>
                <Text style={{ color: '#a0a0ab', fontSize: 11, marginTop: 8, textAlign: 'center' }}>{label}</Text>
            </View>
        );
    };

    return (
        <SafeAreaView style={styles.container}>
            <View style={styles.header}>
                <TouchableOpacity onPress={() => navigation.goBack()}>
                    <ChevronLeftIcon size={28} color="#fff" />
                </TouchableOpacity>
                <Text style={styles.headerTitle}>상세 분석 보고서</Text>
                <View style={{ width: 28 }} />
            </View>

            <ScrollView contentContainerStyle={styles.scrollBody}>
                {/* 종합 분석 결과 */}
                <View style={styles.sectionHeader}>
                    <Text style={styles.detailSectionTitle}>1) 종합 분석 결과</Text>
                </View>
                <View style={styles.chartsRow}>
                    <DonutChart percentage={detailData.totalScore} color="#ff453a" label="딥페이크 가능성" />
                    <DonutChart percentage={detailData.confidence} color="#7c6cfa" label="신뢰도" />
                    <DonutChart percentage={detailData.matchScore} color="#32d74b" label="영상/음성 일치도" />
                </View>

                {/* 영상 분석 */}
                <View style={styles.detailCard}>
                    <Text style={styles.cardTitle}>2) 영상 분석</Text>
                    <View style={styles.infoRow}>
                        <Text style={styles.rowLabel}>조작 가능성:</Text>
                        <Text style={styles.textFake}>91%</Text>
                    </View>
                    <Text style={styles.subLabel}>의심 구간:</Text>
                    {detailData.videoAnomalies.map((text, i) => (
                        <Text key={i} style={styles.anomalyListText}>{text}</Text>
                    ))}
                    <View style={styles.statsRow}>
                        <Text style={styles.statItem}>얼굴 감지율: 94%</Text>
                        <Text style={styles.statItem}>감지 인원: 1명</Text>
                    </View>
                </View>

                {/* 음성 분석 */}
                <View style={styles.detailCard}>
                    <Text style={styles.cardTitle}>3) 음성 분석</Text>
                    <View style={styles.infoRow}>
                        <Text style={styles.rowLabel}>조작 가능성:</Text>
                        <Text style={styles.textFake}>74%</Text>
                    </View>
                    <Text style={styles.subLabel}>의심 구간 :</Text>
                    {detailData.audioAnomalies.map((text, i) => (
                        <Text key={i} style={styles.anomalyListText}>{text}</Text>
                    ))}
                    <Text style={[styles.statItem, { marginTop: 10 }]}>음성 감지율: 88%</Text>
                </View>

                {/* 분석 한계 */}
                <View style={styles.limitCard}>
                    <Text style={styles.limitTitle}>! 분석 한계</Text>
                    <Text style={styles.limitContent}>
                        영상 일부 구간에서 압축 아티팩트로 인해 정확도가 낮을 수 있습니다.
                    </Text>
                </View>

                <View style={{ height: 40 }} />
            </ScrollView>
        </SafeAreaView>
    );
};