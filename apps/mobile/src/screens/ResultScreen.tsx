import React from 'react';
import { View, Text, SafeAreaView, ScrollView, TouchableOpacity, Image } from 'react-native';
import {
    ShareIcon,
    ArrowLeftIcon
} from 'react-native-heroicons/outline';
import { styles } from './ResultScreen.styles';
import { BottomNavigation } from '../components/BottomNavigaton';
import type { MediaTaskResult } from '../api/verifakeApi';

interface ResultRouteParams {
    separatedMedia?: MediaTaskResult;
    thumbnailUri?: string | null;
}

export const ResultScreen = ({ navigation, route }: any) => {
    const { separatedMedia, thumbnailUri } = (route.params || {}) as ResultRouteParams;
    const resultData = {
        status: separatedMedia?.status ?? 'DONE',
        thumbnailUrl: thumbnailUri ?? 'https://via.placeholder.com/400x225',
        summary: '서버에서 AI 추론 없이 업로드 영상을 영상 스트림과 음성 스트림으로 분리했습니다.',
        videoPath: separatedMedia?.video_path ?? '분리된 영상 경로 없음',
        audioPath: separatedMedia?.audio_path ?? '분리된 음성 경로 없음',
    };

    const isDone = resultData.status === 'DONE';

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
                        <View style={[styles.statusBadge, isDone ? styles.bgReal : styles.bgFake]}>
                            <Text style={styles.statusBadgeText}>{resultData.status}</Text>
                        </View>
                    </View>
                </View>

                {/* 결과 요약 */}
                <View style={styles.scoreSection}>
                    <View style={styles.scoreInfo}>
                        <Text style={styles.scoreLabel}>서버 처리 상태</Text>
                        <Text style={[styles.scoreValue, isDone ? styles.textReal : styles.textFake]}>
                            {isDone ? '분리 완료' : '확인 필요'}
                        </Text>
                    </View>
                    <View style={styles.gaugeBar}>
                        <View style={[styles.gaugeFill, { width: isDone ? '100%' : '30%' }, isDone ? styles.bgReal : styles.bgFake]} />
                    </View>
                </View>

                {/* 서버 처리 요약 */}
                <View style={styles.reasonCard}>
                    <Text style={styles.reasonTitle}>서버 처리 요약</Text>
                    <Text style={styles.reasonContent}>{resultData.summary}</Text>
                </View>

                {/* 세부 탐지 항목 */}
                <View style={styles.detailGrid}>
                    <View style={styles.detailItem}>
                        <Text style={styles.detailLabel}>영상 조작</Text>
                        <Text style={[styles.detailValue, styles.textReal]}>AI 미실행</Text>
                    </View>
                    <View style={styles.detailItem}>
                        <Text style={styles.detailLabel}>음성 조작</Text>
                        <Text style={[styles.detailValue, styles.textReal]}>AI 미실행</Text>
                    </View>
                </View>

                <View style={styles.reasonCard}>
                    <Text style={styles.reasonTitle}>분리 파일 경로</Text>
                    <Text style={styles.pathLabel}>영상</Text>
                    <Text style={styles.pathText}>{resultData.videoPath}</Text>
                    <Text style={styles.pathLabel}>음성</Text>
                    <Text style={styles.pathText}>{resultData.audioPath}</Text>
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
