import pytest
from selenium import webdriver


@pytest.fixture(params=["chrome"], scope="class")  # Will execute test with each param
# @pytest.fixture(params=["firefox", "chrome"], scope="class")  # Will execute test with each param
def init_driver(request):
    def create_options(options):
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--ignore-ssl-errors")
        options.add_argument("--start-maximized")
        options.add_argument('--headless')
        options.add_argument('window-size=2560x1440')  # Chrome
        options.add_argument("--width=2560")  # Firefox
        options.add_argument("--height=1440")  # Firefox
        return options

    if request.param == "chrome":
        print("Starting Chrome")
        options = webdriver.ChromeOptions()
        options = create_options(options)
        driver = webdriver.Chrome(executable_path=r"./chromedriver", options=options)

    if request.param == "firefox":
        print("Starting Firefox")
        options = webdriver.FirefoxOptions()
        options = create_options(options)
        driver = webdriver.Firefox(executable_path=r"./geckodriver", options=options)

    request.cls.driver = driver  # So that, to access the driver you write this.driver
    yield
    driver.close()
