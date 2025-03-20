#include <iostream>
#include <vector>
#include <conio.h>
#include <windows.h>
#include <random>

using namespace std;

struct Point {
    int x, y;
};

enum Direction { UP, DOWN, LEFT, RIGHT };

int main() {
    int width = 20;
    int height = 15;
    vector<Point> snake = { {width / 2, height / 2} };
    Direction dir = RIGHT;
    Point food;

    random_device rd;
    mt19937 gen(rd());
    uniform_int_distribution<> distW(0, width - 1);
    uniform_int_distribution<> distH(0, height - 1);

    auto generateFood = [&]() {
        bool onSnake;
        do {
            food.x = distW(gen);
            food.y = distH(gen);
            onSnake = false;
            for (const auto& segment : snake) {
                if (segment.x == food.x && segment.y == food.y) {
                    onSnake = true;
                    break;
                }
            }
        } while (onSnake);
    };

    generateFood();

    bool gameOver = false;

    while (!gameOver) {
        system("cls");

        for (int y = 0; y < height; ++y) {
            for (int x = 0; x < width; ++x) {
                bool isSnakeBody = false;
                for (size_t i = 0; i < snake.size(); ++i) {
                    if (snake[i].x == x && snake[i].y == y) {
                        if (i == 0) {
                            cout << "O";
                        } else {
                            cout << "o";
                        }
                        isSnakeBody = true;
                        break;
                    }
                }
                if (!isSnakeBody) {
                    if (x == food.x && y == food.y) {
                        cout << "F";
                    } else {
                        cout << ".";
                    }
                }
            }
            cout << endl;
        }

        if (_kbhit()) {
            int ch = _getch();
            switch (ch) {
                case 72: if (dir != DOWN) dir = UP; break;
                case 80: if (dir != UP) dir = DOWN; break;
                case 75: if (dir != RIGHT) dir = LEFT; break;
                case 77: if (dir != LEFT) dir = RIGHT; break;
            }
        }

        Point newHead = snake[0];
        switch (dir) {
            case UP: newHead.y--; break;
            case DOWN: newHead.y++; break;
            case LEFT: newHead.x--; break;
            case RIGHT: newHead.x++; break;
        }

        if (newHead.x < 0 || newHead.x >= width || newHead.y < 0 || newHead.y >= height) {
            gameOver = true;
        }

        for (size_t i = 1; i < snake.size(); ++i) {
            if (newHead.x == snake[i].x && newHead.y == snake[i].y) {
                gameOver = true;
                break;
            }
        }

        if (!gameOver)
        {
            snake.insert(snake.begin(), newHead);

            if (newHead.x == food.x && newHead.y == food.y) {
                generateFood();
            } else {
                snake.pop_back();
            }
        }


        Sleep(100);
    }
    system("cls");
    cout << "Game Over!" << endl;
    cout << "Your score: " << snake.size() -1 << endl;
     _getch();

    return 0;
}