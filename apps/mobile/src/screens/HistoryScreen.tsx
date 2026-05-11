import React from 'react';
import { View, Text, SafeAreaView, FlatList, Image, TouchableOpacity } from 'react-native';
import { styles } from './HistoryScreen.styles';
import { BottomNavigation } from '../components/BottomNavigaton';

// 전체 기록 예시 데이터
const ALL_HISTORY_DATA = [
    { id: '1', status: 'FAKE', score: 91.3, title: '정치인 A 인터뷰 조작 의심', date: '2024.05.07 11:20', thumb: 'https://via.placeholder.com/100' },
    { id: '2', status: 'REAL', score: 12.5, title: '뉴스 브리핑 영상', date: '2024.05.07 10:15', thumb: 'https://via.placeholder.com/100' },
    { id: '3', status: 'FAKE', score: 88.7, title: 'SNS 공유 딥페이크 의심 영상', date: '2024.05.06 23:40', thumb: 'https://via.placeholder.com/100' },
    { id: '4', status: 'FAKE', score: 95.2, title: '유명인 사칭 광고 영상', date: '2024.05.06 18:22', thumb: 'https://via.placeholder.com/100' },
];

export const HistoryScreen = ({ navigation }: any) => {
    const renderItem = ({ item }: any) => {
        const isFake = item.status === 'FAKE';

        return (
            <TouchableOpacity
                style={styles.historyCard}
                onPress={() => navigation.navigate('Result')} // 상세 결과 페이지로 이동
            >
                <Image source={{ uri: item.thumb }} style={styles.thumbnail} />

                <View style={styles.infoContainer}>
                    <View style={[styles.statusBadge, isFake ? styles.bgFake : styles.bgReal]}>
                        <Text style={styles.statusText}>{item.status}</Text>
                    </View>
                    <Text style={styles.videoTitle} numberOfLines={1}>{item.title}</Text>
                    <Text style={styles.dateText}>{item.date}</Text>
                </View>

                <View style={styles.scoreContainer}>
                    <Text style={[styles.scoreValue, isFake ? styles.textFake : styles.textReal]}>
                        {item.score}%
                    </Text>
                </View>
            </TouchableOpacity>
        );
    };

    return (
        <SafeAreaView style={styles.container}>
            <View style={styles.header}>
                <Text style={styles.headerTitle}>전체 탐지 기록</Text>
            </View>

            <FlatList
                data={ALL_HISTORY_DATA}
                renderItem={renderItem}
                keyExtractor={item => item.id}
                contentContainerStyle={styles.listContent}
                showsVerticalScrollIndicator={false}
            />

            <BottomNavigation activeRoute="History" />
        </SafeAreaView>
    );
};