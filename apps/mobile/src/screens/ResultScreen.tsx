import React from 'react';
import { View, Text, SafeAreaView, ScrollView, TouchableOpacity, Image } from 'react-native';
import {
    ShareIcon,
    ArrowLeftIcon
} from 'react-native-heroicons/outline';
import { styles } from './ResultScreen.styles';
import { BottomNavigation } from '../components/BottomNavigaton';

export const ResultScreen = ({ navigation }: any) => {
    const resultData = {
        status: 'FAKE',
        score: 91.3,
        thumbnailUrl: 'https://via.placeholder.com/400x225', // 분석한 영상 썸네일
        llmReason: "얼굴 경계선에서 블렌딩 아티팩트가 감지되었으며, 눈 깜빡임 패턴이 자연스럽지 않습니다. 음성 피치와 입 모양의 싱크가 0.3초 어긋나 있으며, 배경 조명과 피부톤 반사를 통해 불일치가 확인됩니다.",
        videoDetection: "감지됨",
        audioDetection: "감지됨",
        cacheHit: "미스"
    };

    const isFake = resultData.status === 'FAKE';

    return (
        <SafeAreaView style={styles.container}>
            {/* 헤더 */}
            <View style={styles.header}>
                <TouchableOpacity onPress={() => navigation.navigate('Home')} style={styles.backBtn}>
                    <ArrowLeftIcon size={24} color="#7c6cfa" />
                </TouchableOpacity>
                <Text style={styles.headerTitle}>분석 결과</Text>
                <View style={{ width: 24 }} />
            </View>

            <ScrollView contentContainerStyle={styles.body}>
                {/* 분석 */}
                <View style={styles.mediaPreview}>
                    <Image
                        source={{ uri: resultData.thumbnailUrl }}
                        style={styles.previewImage}
                        resizeMode="cover"
                    />
                    <View style={styles.mediaOverlay}>
                        <View style={[styles.statusBadge, isFake ? styles.bgFake : styles.bgReal]}>
                            <Text style={styles.statusBadgeText}>{resultData.status}</Text>
                        </View>
                    </View>
                </View>

                {/* 결과 요약 */}
                <View style={styles.scoreSection}>
                    <View style={styles.scoreInfo}>
                        <Text style={styles.scoreLabel}>탐지 신뢰도</Text>
                        <Text style={[styles.scoreValue, isFake ? styles.textFake : styles.textReal]}>
                            {resultData.score}%
                        </Text>
                    </View>
                    <View style={styles.gaugeBar}>
                        <View style={[styles.gaugeFill, { width: `${resultData.score}%` }, isFake ? styles.bgFake : styles.bgReal]} />
                    </View>
                </View>

                {/* LLM 분석 근거 */}
                <View style={styles.reasonCard}>
                    <Text style={styles.reasonTitle}>LLM 분석 근거</Text>
                    <Text style={styles.reasonContent}>{resultData.llmReason}</Text>
                </View>

                {/* 세부 탐지 항목 */}
                <View style={styles.detailGrid}>
                    <View style={styles.detailItem}>
                        <Text style={styles.detailLabel}>영상 조작</Text>
                        <Text style={[styles.detailValue, isFake ? styles.textFake : styles.textReal]}>{resultData.videoDetection}</Text>
                    </View>
                    <View style={styles.detailItem}>
                        <Text style={styles.detailLabel}>음성 조작</Text>
                        <Text style={[styles.detailValue, isFake ? styles.textFake : styles.textReal]}>{resultData.audioDetection}</Text>
                    </View>
                </View>

                <TouchableOpacity style={styles.shareBtn}>
                    <ShareIcon size={20} color="#fff" style={{ marginRight: 8 }} />
                    <Text style={styles.shareBtnText}>결과 공유하기</Text>
                </TouchableOpacity>
            </ScrollView>

            <BottomNavigation activeRoute="DetectionInput" />
        </SafeAreaView>
    );
};