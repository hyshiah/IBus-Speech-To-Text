#!/usr/bin/env python3
# generate by deepseek
from gi.repository import Gio, GLib
import sys

class PromptInterface:
    def __init__(self):
        self.x = 0
        self.y = 0

class DbusTestService:
    def __init__(self):
        # 註冊總線名稱
        # SERVICE_NAME = 'org.test.shiah'
        self.connection = Gio.bus_get_sync(Gio.BusType.SESSION, None)
        self.owner_id = Gio.bus_own_name_on_connection(
            self.connection,
            'org.test.shiah',
            Gio.BusNameOwnerFlags.NONE,
            None,
            None
        )
        
        # 創建主對象
        self.setup_main_object()
        
        # 創建 prompt 子對象
        self.prompt_interface = PromptInterface()
        self.setup_prompt_object()

    def setup_main_object(self):
        """設置主對象 /com/test/shiah/dbustest"""
        main_object_info = Gio.DBusNodeInfo.new_for_xml("""
            <node>
                <interface name='org.test.shiah.Main'>
                    <method name='Ping'>
                        <arg type='s' name='message' direction='in'/>
                        <arg type='s' name='response' direction='out'/>
                    </method>
                </interface>
            </node>
        """)
        
        self.connection.register_object(
            '/com/test/shiah/dbustest',
            main_object_info.interfaces[0],
            self.handle_main_method_call,
            None
        )

    def setup_prompt_object(self):
        """設置 prompt 對象 /com/test/shiah/dbustest/prompt"""
        prompt_object_info = Gio.DBusNodeInfo.new_for_xml("""
            <node>
                <interface name='org.test.shiah.Prompt'>
                    <method name='Exit'/>
                    <method name='UpdateCoordinates'>
                        <arg type='i' name='x' direction='in'/>
                        <arg type='i' name='y' direction='in'/>
                    </method>
                    <method name='GetCoordinates'>
                        <arg type='i' name='x' direction='out'/>
                        <arg type='i' name='y' direction='out'/>
                    </method>
                    <signal name='CoordinatesChanged'>
                        <arg type='i' name='x'/>
                        <arg type='i' name='y'/>
                    </signal>
                </interface>
            </node>
        """)
        
        self.connection.register_object(
            '/com/test/shiah/dbustest/prompt',
            prompt_object_info.interfaces[0],
            self.handle_prompt_method_call,
            None
        )

    def handle_main_method_call(self, connection, sender, object_path, interface_name, method_name, parameters, invocation):
        """處理主對象的方法呼叫"""
        if method_name == 'Ping':
            message = parameters.get_child_value(0).get_string()
            print(f"收到 Ping: {message}")
            invocation.return_value(GLib.Variant('(s)', ['Pong: ' + message]))
        else:
            invocation.return_dbus_error('org.test.shiah.Error', '未知方法')

    def handle_prompt_method_call(self, connection, sender, object_path, interface_name, method_name, parameters, invocation):
        """處理 prompt 對象的方法呼叫"""
        if method_name == 'Exit':
            print("收到 Exit 信號，準備結束程式...")
            invocation.return_value(None)
            GLib.timeout_add(100, self.quit_program)
            
        elif method_name == 'UpdateCoordinates':
            x = parameters.get_child_value(0).get_int32()
            y = parameters.get_child_value(1).get_int32()
            self.prompt_interface.x = x
            self.prompt_interface.y = y
            print(f"滑鼠座標更新: X={x}, Y={y}")
            
            # 發送信號通知座標改變
            self.connection.emit_signal(
                None,
                '/com/test/shiah/dbustest/prompt',
                'org.test.shiah.Prompt',
                'CoordinatesChanged',
                GLib.Variant.new_tuple(
                    GLib.Variant('i', x),
                    GLib.Variant('i', y)
                )
            )
            invocation.return_value(None)
            
        elif method_name == 'GetCoordinates':
            x = self.prompt_interface.x
            y = self.prompt_interface.y
            print(f"查詢當前座標: X={x}, Y={y}")
            invocation.return_value(GLib.Variant('(ii)', [x, y]))
            
        else:
            invocation.return_dbus_error('org.test.shiah.Error', '未知方法')

    def quit_program(self):
        """結束程式"""
        print("結束 D-Bus 服務")
        loop.quit()
        return False

def main():
    print("啟動 Gio D-Bus 服務...")
    print("服務名稱: org.test.shiah")
    print("對象路徑: /com/test/shiah/dbustest")
    print("子對象路徑: /com/test/shiah/dbustest/prompt")
    print("\n可用方法:")
    print("  - Ping(message): 測試連接")
    print("  - Exit(): 結束程式")
    print("  - UpdateCoordinates(x, y): 更新座標")
    print("  - GetCoordinates(): 獲取當前座標")
    print("\n使用以下命令測試:")
    
    print("1. 測試 Ping:")
    print("dbus-send --session --type=method_call --print-reply \\")
    print("  --dest=org.test.shiah /com/test/shiah/dbustest \\")
    print("  org.test.shiah.Main.Ping string:'Hello'")
    
    print("\n2. 發送滑鼠座標:")
    print("dbus-send --session --type=method_call --print-reply \\")
    print("  --dest=org.test.shiah /com/test/shiah/dbustest/prompt \\")
    print("  org.test.shiah.Prompt.UpdateCoordinates int32:100 int32:200")
    
    print("\n3. 獲取座標:")
    print("dbus-send --session --type=method_call --print-reply \\")
    print("  --dest=org.test.shiah /com/test/shiah/dbustest/prompt \\")
    print("  org.test.shiah.Prompt.GetCoordinates")
    
    print("\n4. 關閉服務:")
    print("dbus-send --session --type=method_call --print-reply \\")
    print("  --dest=org.test.shiah /com/test/shiah/dbustest/prompt \\")
    print("  org.test.shiah.Prompt.Exit")
    
    print("\n5. 監聽座標改變信號:")
    print("dbus-monitor --session \\")
    print("  \"type='signal',interface='org.test.shiah.Prompt',path='/com/test/shiah/dbustest/prompt'\"")
    
    print("\n等待 D-Bus 呼叫...")
    
    global loop
    try:
        service = DbusTestService()
        loop = GLib.MainLoop()
        loop.run()
    except KeyboardInterrupt:
        print("\n收到 Ctrl+C，結束程式...")
    except Exception as e:
        print(f"錯誤: {e}")
    finally:
        if 'service' in locals():
            Gio.bus_unown_name(service.owner_id)

if __name__ == '__main__':
    main()
