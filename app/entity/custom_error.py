class CustomError(Exception):
    """自定义异常基类"""

    def __init__(self, message: str, code: int = 400):
        """
        Args:
            message: 错误信息
            code: 错误状态码(默认400)
        """
        self.message = message
        self.code = code
        super().__init__(message)

    def __str__(self):
        return f"[Error {self.code}] {self.message}"
