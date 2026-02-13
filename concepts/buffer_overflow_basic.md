# Buffer Overflow Basic

## 문제 유형
기본 BOF, 인접 변수 덮어쓰기

## 핵심 코드 구조
char buf[32];
int win = 0;

## 풀이 요약
"A"*100 입력 → win 변수 덮어짐 → flag 출력

## 배운 점
- overflow는 return address만 건드는 게 아니다
- 변수도 덮을 수 있다
