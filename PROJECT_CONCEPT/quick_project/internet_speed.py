import speedtest

if __name__ == '__main__':
    dir(speedtest)
    speed = speedtest()
    download_speed = speed.download()
    upload_speed = speed.upload()
    print(f'The download speed is {download_speed}')
    print(f'The uplaod speed is {upload_speed}')
