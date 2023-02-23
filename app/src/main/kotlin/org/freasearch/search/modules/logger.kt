package org.freasearch.search.logger


public class ConsoleColors (){
    val RESET = "\u001B[0m"
    val BOLD = "\u001B[1m"

    val RED = "\u001B[31m"
    val GREEN = "\u001B[32m"
    val YELLOW = "\u001B[33m"
    val BLUE = "\u001B[34m"

    val RED_BOLD = "\u001B[1m\u001B[31m"
    val GREEN_BOLD = "\u001B[1m\u001B[32m"
    val YELLOW_BOLD = "\u001B[1m\u001B[33m"
    val BLUE_BOLD = "\u001B[1m\u001B[「34m"

    //アンダーライン付き（callerPackageName表示用）
    val WHITE = "\u001B[4m\u001B[37m"
}


val callerPackageName = Throwable().stackTrace[1].className.substringBeforeLast('.')
val color = ConsoleColors()

fun msg_info(msg: String) {
    System.out.println("${color.GREEN_BOLD}[INFO] ${color.WHITE}${callerPackageName}${color.RESET} ${msg}")
}

fun msg_warn(msg: String) {
    System.out.println("${color.YELLOW_BOLD}[WARNING] ${color.WHITE}${callerPackageName}${color.RESET} ${msg}")
}

fun msg_error(msg: String) {
    System.err.println("${color.RED_BOLD}[ERROR] ${color.WHITE}${callerPackageName}${color.RESET} ${color.RED}${msg}${color.RESET}")
}
