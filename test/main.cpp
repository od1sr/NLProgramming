#include <iostream>
#include <string>
#include <vector>
#include <stdexcept>
#include <cctype>
#include <cmath>
#include <limits> // Required for numeric_limits

class Parser {
    std::string input;
    size_t pos = 0;

    void skip_whitespace() {
        while (pos < input.length() && std::isspace(input[pos])) {
            pos++;
        }
    }

    char peek() const {
        if (pos < input.length()) {
            return input[pos];
        }
        return '\0';
    }

    char get() {
         if (pos < input.length()) {
            return input[pos++];
        }
        return '\0';
    }

    double parse_number() {
        skip_whitespace();
        size_t start_pos = pos;
        bool has_decimal = false;
        while (pos < input.length() && (std::isdigit(input[pos]) || input[pos] == '.')) {
             if (input[pos] == '.') {
                if (has_decimal) throw std::runtime_error("Invalid number format: multiple decimal points");
                has_decimal = true;
            }
            pos++;
        }
         if (pos == start_pos) {
             throw std::runtime_error("Expected number at position " + std::to_string(start_pos));
         }

        try {
            return std::stod(input.substr(start_pos, pos - start_pos));
        } catch (const std::out_of_range&) {
            throw std::runtime_error("Number out of range at position " + std::to_string(start_pos));
        } catch (...) {
             throw std::runtime_error("Invalid number format near position " + std::to_string(start_pos));
        }
    }

    double parse_factor() {
        skip_whitespace();
        char current = peek();

        if (current == '(') {
            get(); // Consume '('
            double result = parse_expression();
            skip_whitespace();
            if (peek() != ')') {
                throw std::runtime_error("Mismatched parentheses: expected ')'");
            }
            get(); // Consume ')'
            return result;
        } else if (current == '-') {
            get(); // Consume '-'
            return -parse_factor(); // Unary minus
        } else if (current == '+') {
             get(); // Consume '+'
             return parse_factor(); // Unary plus (optional, usually ignored)
        } else if (std::isdigit(current) || current == '.') {
            return parse_number();
        } else {
             if (pos >= input.length()) {
                 throw std::runtime_error("Unexpected end of input, expected factor");
             } else {
                throw std::runtime_error("Unexpected character '" + std::string(1, current) + "' at position " + std::to_string(pos) + ", expected number, parenthesis or unary sign");
             }
        }
    }

    double parse_term() {
        double left = parse_factor();
        while (true) {
            skip_whitespace();
            char op = peek();
            if (op == '*' || op == '/') {
                get(); // Consume operator
                double right = parse_factor();
                if (op == '*') {
                    left *= right;
                } else {
                    if (std::abs(right) < std::numeric_limits<double>::epsilon()) {
                        throw std::runtime_error("Division by zero");
                    }
                    left /= right;
                }
            } else {
                break;
            }
        }
        return left;
    }

    double parse_expression() {
        double left = parse_term();
        while (true) {
            skip_whitespace();
            char op = peek();
            if (op == '+' || op == '-') {
                get(); // Consume operator
                double right = parse_term();
                if (op == '+') {
                    left += right;
                } else {
                    left -= right;
                }
            } else {
                break;
            }
        }
        return left;
    }

public:
    Parser(const std::string& expr) : input(expr), pos(0) {}

    double calculate() {
        pos = 0; // Reset position for potential reuse
        if (input.empty()) {
            throw std::runtime_error("Empty expression");
        }
        double result = parse_expression();
        skip_whitespace();
        if (pos < input.length()) {
            throw std::runtime_error("Unexpected character '" + std::string(1, input[pos]) + "' after expression at position " + std::to_string(pos));
        }
        return result;
    }
};

int main() {
    std::string expression;
    std::cout << "Enter expression (or empty line to exit): ";
    while (std::getline(std::cin, expression) && !expression.empty()) {
        try {
            Parser p(expression);
            double result = p.calculate();
            std::cout << "Result: " << result << std::endl;
        } catch (const std::exception& e) {
            std::cerr << "Error: " << e.what() << std::endl;
        }
         std::cout << "\nEnter expression (or empty line to exit): ";
    }
    return 0;
}