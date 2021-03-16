import java.util.Scanner;

public class InputPrimNum {
	public static void main(String[] args) {

		System.out.println("숫자를 입력하세요.");
		Scanner s = new Scanner(System.in);
		int inputNum = s.nextInt(); //숫자입력받기 

		int countNum = 0;			//카운트 넘버 정의 

		//for문 - 입력값까지 숫자 생성
		for (int i = 0; i < inputNum; i++) {  
			int num = i + 1;
			
			//if 문 만약 1이거나 자시자신이면 패스 
			//else if 입력값 % 생성값 의 나머지가 0 이면 카운트에 1을 더해라 (포문 종료)
			if (num == 1 || num == inputNum) {
				continue;
			} else if (inputNum % num == 0) {
				countNum = countNum + 1;
			}
		}
		// 카운트 값이 0이면 소수 그 이상이면 소수가 아니다. (하나라도 나눠지면 소수가 아니기 때문에)
		if (countNum == 0) {
			System.out.println("소수입니다.");
		} else {
			System.out.println("소수가 아닙니다.");
		}
	}
}
