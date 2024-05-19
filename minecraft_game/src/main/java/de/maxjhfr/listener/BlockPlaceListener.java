package de.maxjhfr.listener;

import net.md_5.bungee.api.ChatColor;

import java.net.URI;
import java.net.URISyntaxException;

import org.bukkit.entity.Entity;
import org.bukkit.entity.EntityType;
import org.bukkit.entity.Player;
import org.bukkit.event.EventHandler;
import org.bukkit.event.Listener;
import org.bukkit.event.entity.EntityPlaceEvent;

import de.maxjhfr.Main;
import de.maxjhfr.webSocket.MinecraftToFlask;
import de.maxjhfr.webSocket.MyWebSocketClient;

public class BlockPlaceListener implements Listener {

    private Main plugin;

    public BlockPlaceListener(Main plugin) {
        this.plugin = plugin;
    }


    @EventHandler
    public void onBlockPlace(EntityPlaceEvent e) {
        Entity entity = e.getEntity();
        Player p = e.getPlayer();
        if (entity.getType().equals(EntityType.ARMOR_STAND) & entity.getLocation().getY() >= 100) {
            e.setCancelled(false);
            p.sendMessage(ChatColor.GREEN + "Gut gemacht! Du hast jetzt wieder Empfang und du sendest auf Leitung "
                        + ChatColor.BLUE + '7');
                   
            new MinecraftToFlask().sendPostRequest("minecraft", "done");

        } else {
            e.setCancelled(true);
            p.sendMessage(ChatColor.RED + "Die Antenne ist nicht hoch genug");
        }
    }



}
