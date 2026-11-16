import React, {useRef, useState} from 'react';
import {ActivityIndicator, Pressable, ScrollView, StatusBar, StyleSheet, Text, View} from 'react-native';

const api = process.env.EXPO_PUBLIC_API_URL || 'http://10.0.2.2:8000';
const labels = {today: 'DZISIAJ', tomorrow: 'JUTRO'};
const states = {
  TRENUJ: {label: 'TRENUJ', color: '#96efb5', surface: '#203c32'},
  OGRANICZ: {label: 'OGRANICZ', color: '#ffdb76', surface: '#443b24'},
  'ZOSTAŃ W DOMU': {label: 'NIE TRENUJ', color: '#ff9f9e', surface: '#472c32'},
};
const missing = {label: 'BRAK DANYCH', color: '#bbc4cc', surface: '#333942'};

function HourCard({row, time, expanded, onPress}) {
  const status = states[row.message] || missing;
  const rating = row.score == null ? '—' : row.score;
  const details = [
    ['PM10 · średnia dobowa', row.pm10_daily_mean, 'µg/m³'],
    ['Temperatura', row.temperature_2m, '°C'],
    ['Wiatr', row.wind_speed_10m, 'km/h'],
    ['Opady', row.precipitation, 'mm'],
  ];
  return <View style={[styles.card, expanded && styles.expanded]}>
    <Pressable onPress={onPress} accessibilityRole="button" accessibilityState={{expanded}}
      accessibilityLabel={time + ', ' + (row.score == null ? '' : rating + '/100, ') + status.label}
      accessibilityHint="Pokaż lub ukryj szczegóły godziny"
      android_ripple={{color:'#304239'}} style={styles.cardButton}>
      <View style={styles.summary}>
        <Text style={styles.time}>{time}</Text>
        <View style={[styles.badge,{backgroundColor:status.surface}]}>
          <View style={[styles.dot,{backgroundColor:status.color}]}/>
          <Text style={[styles.badgeText,{color:status.color}]}>{status.label}</Text>
        </View>
      </View>
      <View style={styles.rating}>
        <Text style={[styles.number,{color:status.color}]}>{rating}</Text>
        {row.score != null && <Text style={styles.scale}>/100</Text>}
      </View>
      <View style={[styles.chevron,{transform:[{rotate:expanded ? '225deg' : '45deg'}]}]}/>
    </Pressable>
    {expanded && <View style={styles.details}>
      {details.map(([name,value,unit]) => <View key={name} style={styles.metric}>
        <Text style={styles.metricName}>{name}</Text>
        <Text style={styles.metricValue}>{value == null ? 'Brak danych' : String(value).replace('.', ',') + ' ' + unit}</Text>
      </View>)}
    </View>}
  </View>;
}

export default function App() {
  const [day, setDay] = useState('today');
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const busy = useRef(false);
  const [expanded, setExpanded] = useState(null);

  function select(value) {
    if (busy.current || value === day) return;
    setDay(value);
    setExpanded(null);
    setResult(null);
    setError('');
  }
  async function check() {
    if (busy.current) return;
    busy.current = true;
    setLoading(true);
    setExpanded(null);
    setResult(null);
    setError('');
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 40000);
    try {
      const response = await fetch(api + '/forecast/' + day, {signal: controller.signal});
      if (!response.ok) {
        const body = await response.json();
        throw new Error(typeof body.detail === 'string' ? body.detail : 'Błąd odpowiedzi FastAPI.');
      }
      setResult(await response.json());
    } catch (e) {
      setError(e.message === 'Network request failed' || e.name === 'AbortError'
        ? 'Brak połączenia z FastAPI. Sprawdź adres backendu i ponów próbę.' : e.message);
    } finally {
      clearTimeout(timer);
      busy.current = false;
      setLoading(false);
    }
  }
  return <ScrollView style={styles.page} contentContainerStyle={styles.content}>
    <StatusBar translucent={false} barStyle="light-content" backgroundColor="#101a20"/>
    <View style={styles.controls}>{Object.entries(labels).map(([key, label]) =>
      <Pressable key={key} disabled={loading} accessibilityRole="button"
        accessibilityState={{selected:day === key, disabled:loading}} onPress={() => select(key)}
        style={[styles.segment, day === key && styles.selected]}>
        <Text style={[styles.tabText, day === key && styles.selectedText]}>{label}</Text>
      </Pressable>)}</View>
    <Pressable disabled={loading} accessibilityRole="button" accessibilityState={{disabled:loading}}
      onPress={check} android_ripple={{color:'#b5e68c'}} style={styles.check}>
      {loading && <ActivityIndicator color="#172318"/>}
      <Text style={styles.checkText}>{loading ? 'Pobieranie…' : 'SPRAWDŹ'}</Text>
    </Pressable>
    {!!error && <Text accessibilityRole="alert" style={styles.notice}>{error}</Text>}
    {result && Object.values(result.origin).includes('cache') && <Text style={styles.muted}>Dane zapisane wcześniej</Text>}
    {result && result.hours.map(row => <HourCard key={row.timestamp_utc} row={row}
      time={row.timestamp.slice(11,16) + (result.hours.length > 24 ? ' ' + row.timestamp.slice(16) : '')}
      expanded={expanded === row.timestamp_utc}
      onPress={() => setExpanded(previous => previous === row.timestamp_utc ? null : row.timestamp_utc)}/>)}
  </ScrollView>;
}

const styles = StyleSheet.create({
  page:{flex:1,backgroundColor:'#101a20'},
  content:{paddingHorizontal:18,paddingTop:22,paddingBottom:38,gap:10},
  controls:{flexDirection:'row',padding:4,borderRadius:16,backgroundColor:'#1b2931'},
  segment:{flex:1,minHeight:45,alignItems:'center',justifyContent:'center',borderRadius:12},
  selected:{backgroundColor:'#364953'},
  tabText:{fontSize:13,fontWeight:'700',letterSpacing:1.2,color:'#aebdc4'},
  selectedText:{color:'#fff'},
  check:{minHeight:50,borderRadius:16,backgroundColor:'#d2f5a3',flexDirection:'row',
    alignItems:'center',justifyContent:'center',gap:10,marginBottom:8},
  checkText:{fontSize:15,fontWeight:'900',letterSpacing:1.1,color:'#152415'},
  card:{backgroundColor:'#1a282f',borderRadius:18,borderWidth:1,borderColor:'#2b3a42',overflow:'hidden'},
  expanded:{borderColor:'#708a83'},
  cardButton:{minHeight:92,flexDirection:'row',alignItems:'center',paddingHorizontal:18,paddingVertical:12,gap:12},
  summary:{flex:1,gap:5,alignItems:'flex-start'},
  time:{color:'#f1f6f7',fontSize:21,fontWeight:'600',fontVariant:['tabular-nums']},
  badge:{flexDirection:'row',alignItems:'center',gap:6,paddingHorizontal:8,paddingVertical:4,borderRadius:7},
  dot:{width:6,height:6,borderRadius:3},
  badgeText:{fontWeight:'800',fontSize:11,letterSpacing:0.7},
  rating:{flexDirection:'row',alignItems:'baseline'},
  number:{fontWeight:'900',fontSize:42,letterSpacing:-1.6,fontVariant:['tabular-nums']},
  scale:{fontSize:14,fontWeight:'600',color:'#b4c1c6'},
  chevron:{width:9,height:9,borderRightWidth:2,borderBottomWidth:2,borderColor:'#adbec3',marginLeft:2},
  details:{marginHorizontal:18,borderTopColor:'#38474e',borderTopWidth:1,paddingVertical:8},
  metric:{flexDirection:'row',justifyContent:'space-between',gap:10,paddingVertical:5},
  metricName:{flexShrink:1,fontSize:14,color:'#bccbd0'},
  metricValue:{fontSize:15,fontWeight:'700',color:'#f0f5f6'},
  muted:{color:'#b4c1c6'},notice:{color:'#ffb6aa'}
});
